from  Adafruit_IO import  MQTTClient
import queue
import time
import json
import threading

MAX_SIZE_WHOS = 20
TOPIC_SUBSRIBES = [
    "iotdemo.who",
    "iotdemo.ledmessage",
    "iotdemo.images"
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
    # print('Feed {0} received new value: {1}'.format(feed_id, payload))
    
    client.lockData.acquire()

    if feed_id == "iotdemo.who":
        if client.whoQueue.qsize() >= MAX_SIZE_WHOS:
            client.whoQueue.get()
        client.whoQueue.put({
            "timestamp": str(time.time()),
            "payload": payload
        })
        client.signalChange[0] = 1

    
    if feed_id == "iotdemo.ledmessage":
        client.ledMessage = {
            "timestamp": str(time.time()),
            "payload": payload
        }
        client.signalChange[1] = 1

    if feed_id == "iotdemo.images":
        try:
            client.lastImage = {
                "timestamp": str(time.time()),
                "payload": json.loads(payload)
            }
        except Exception as e:
            print("Load image json failed: ", str(e))
        client.signalChange[2] = 1
    
    client.lockData.release()

class IoTClient(object):

    def __init__(self):
        self.__ADAFRUIT_IO_USERNAME = "trild97"
        self.__ADAFRUIT_IO_KEY = "aio_yECT83ZdYPaNPFeIHjftYgWyuiY5"

        # Create an MQTT client instance.
        self.client = MQTTClient(self.__ADAFRUIT_IO_USERNAME, self.__ADAFRUIT_IO_KEY)
        
        self.client.whoQueue = queue.Queue()
        self.client.ledMessage = ""
        self.client.lastImage = {}
        self.client.signalChange = [0, 0, 0]
        self.client.lockData = threading.Lock()

        # Setup the callback functions defined above.
        self.client.on_connect    = connected
        self.client.on_disconnect = disconnected
        self.client.on_message    = message


    def start(self):
        # Connect to the Adafruit IO server.
        self.client.connect()
        self.client.loop_background()

    def __reconnection(self):
        self.client.disconnect()

        self.client.connect()
        self.client.loop_background()

    def stop(self):
        # Disconnect to the Adafruit IO server.
        self.client.disconnect()

    def getQueueData(self):
        data = {}
        self.client.lockData.acquire()
        for index, topic in enumerate(TOPIC_SUBSRIBES): 
            if self.client.signalChange[index]:
                self.client.signalChange[index] = 0
                if topic == "iotdemo.who":
                    data[topic] = list(self.client.whoQueue.queue)
                elif topic == "iotdemo.ledmessage":
                    data[topic] = self.client.ledMessage
                elif topic == "iotdemo.images":
                    data[topic] = self.client.lastImage
        self.client.lockData.release()

        return data
    
    def publishLEDMessage(self, mes):
        try:
            self.client.publish("iotdemo.control", json.dumps({
                "cmd": "showMessage",
                "arg": [mes]
            }))
        except Exception as e:
            print("Got error with adafruit: ", str(e))
            self.__reconnection()

    def publishNewGuest(self, name, id):
        try:
            self.client.publish("iotdemo.control", json.dumps({
                "cmd": "addNewGuest",
                "arg": [name, id]
            }))
        except Exception as e:
            print("Got error with adafruit: ", str(e))
            self.__reconnection()