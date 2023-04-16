import datetime
import json
from  Adafruit_IO import  MQTTClient
from FaceRecognition import FaceAI
from Utils import *
TOPIC_SUBSRIBES = [
    "iotdemo.control"
]

# Define callback functions which will be called when certain events happen.
def connected(client):
    print('Connected to Adafruit IO!  Listening for iotdemo changes...')
    for topic in TOPIC_SUBSRIBES:
        client.subscribe(topic)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

    if feed_id == "iotdemo.control":
        client.cmdControl = payload

class IoTServer(object):

    def __init__(self):
        self.__ADAFRUIT_IO_USERNAME = "trild97"
        self.__ADAFRUIT_IO_KEY = "aio_yECT83ZdYPaNPFeIHjftYgWyuiY5"

        # Create an MQTT client instance.
        self.client = MQTTClient(self.__ADAFRUIT_IO_USERNAME, self.__ADAFRUIT_IO_KEY)

        # Setup the callback functions defined above.
        self.client.on_connect    = connected
        self.client.on_disconnect = disconnected
        self.client.on_message    = message

        self.client.cmdControl = ""

        self.__LED_TOPIC = "iotdemo.ledmessage"
        self.__OVERSEAS_TOPIC = "iotdemo.overseastimeseries"
        self.__WHO_TOPIC = "iotdemo.who"
        self.__IMAGES_TOPIC = "iotdemo.images"

        self.__iWidth = 96
        self.__iHeight = 128

        self.poolOverseasData = queue.Queue()
        self.poolMutex = threading.Lock()

        self.faceEngine = FaceAI()

        PUBLISH_RAWDATA_INTERVAL = 5
        self.__threadHandleOverseasData = CustomThread(
            handler=self.funcHandleOverseasData, delay=PUBLISH_RAWDATA_INTERVAL)

    def funcHandleOverseasData(self):
        self.poolMutex.acquire()
        # calculate the average value of the numbers in the queue
        try:
            total = 0
            count = self.poolOverseasData.qsize()
            while not self.poolOverseasData.empty():
                num = self.poolOverseasData.get()
                total += num
            if count > 0:
                avg = total / count
                self.client.publish(self.__OVERSEAS_TOPIC, avg)
                print("Publish {1} OverseasData avg {0}".format(avg, count))
            else:
                print("Queue is empty")
        except Exception as e:
            print("Got error with adafruit: ", str(e))
            self.__reconnection()
        
        self.poolMutex.release()

    def start(self):
        # Connect to the Adafruit IO server.
        self.client.connect()
        self.client.loop_background()

        self.__threadHandleOverseasData.start()

    def stop(self):
        # Disconnect to the Adafruit IO server.
        self.__threadHandleOverseasData.set_stop(True)
        self.__threadHandleOverseasData.join()

        self.client.disconnect()

    def __reconnection(self):
        self.client.disconnect()

        self.client.connect()
        self.client.loop_background()


    def pushOverseasData(self, value):
        self.poolMutex.acquire()
        self.poolOverseasData.put(value)
        self.poolMutex.release()
        
    def pushWellcomeGuest(self, name, roiFace):
        try:
            roiFace = cv2.resize(roiFace, (self.__iWidth, self.__iHeight))
            retval, buffer = cv2.imencode('.jpg', roiFace)
            faceBase64 = base64.b64encode(buffer).decode()
            imageData = {
                "name": name,
                "image": faceBase64
            }
            self.client.publish(self.__IMAGES_TOPIC, json.dumps(imageData))
            self.pushLEDMessage("Hi, {0}!".format(name))
            self.client.publish(self.__WHO_TOPIC, 
                    "Wellcome {0} at {1}".format(name, str(datetime.datetime.now())))

        except Exception as e:
            print("Got error with adafruit: ", str(e))
            self.__reconnection()
    
    def pushUnknowGuest(self, roiFace, saveFolder):
        try:
            nameId = "{}.jpg".format(str(time.time()))
            cv2.imwrite(os.path.join(saveFolder, nameId), roiFace)
            roiFace = cv2.resize(roiFace, (self.__iWidth, self.__iHeight))
            retval, buffer = cv2.imencode('.jpg', roiFace)
            faceBase64 = base64.b64encode(buffer).decode()
            imageData = {
                "name": nameId,
                "image": faceBase64
            }
            self.client.publish(self.__IMAGES_TOPIC, json.dumps(imageData))

            self.client.publish(self.__LED_TOPIC, "Unknow guest!")
            self.client.publish(self.__WHO_TOPIC,
                    "Unknow guest at {0}".format(str(datetime.datetime.now())))
        except Exception as e:
            print("Got error with adafruit: ", str(e))
            self.__reconnection()
        
    def recordNewGuest(self, roiFace):
        
        pass

    def pushLEDMessage(self, mes):
        try:
            self.client.publish(self.__LED_TOPIC, mes)
        except Exception as e:
            print("Got error with adafruit: ", str(e))
            self.__reconnection()

    def getCommandControl(self):
        cmd = {}
        if self.client.cmdControl:
            try:
                cmd = json.loads(self.client.cmdControl)
                self.client.cmdControl = ""
            except Exception as e:
                print("Get command control error: ", str(e))
        return cmd