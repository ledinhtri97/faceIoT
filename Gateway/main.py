import serial
import signal
from AdafruitCloud import IoTServer

ser = serial.Serial('/dev/ttyUSB0', 9600) # replace with the correct serial port and baud rate
iotServer = IoTServer()
SENSOR_THRESHOLD = 500

def signal_handler(sig, frame):
    print("Received SIGINT. Exiting...")
    global iotServer
    iotServer.stop()
    exit(0)

def lcdShow(msg):
    print("LCD Show: ", msg)
    cmd = "$lcdshow|{}".format(msg)
    ser.write(cmd.encode())

def processValueSensor(value):
    iotServer.pushOverseasData(value)
    if value < SENSOR_THRESHOLD:
        nameGuest, roiFace = iotServer.faceEngine.predictGuest()
        if nameGuest is not None:
            lcdShow("Hi, {}!".format(nameGuest))
            iotServer.pushWellcomeGuest(nameGuest, roiFace)
        elif roiFace is not None:
            lcdShow("Unknow guest!")
            iotServer.pushUnknowGuest(roiFace, iotServer.faceEngine.unknowPath)
        else:
            lcdShow("No people!")

def main():
    iotServer.start()
    while True:
        if ser.in_waiting > 0:
            data = ser.readline()
            data = data.decode().strip()
            # print("data: ", data)
            values = data.split("#s0!")
            if len(values) > 1:
                value = int(values[1])
                processValueSensor(value)

            cmdControl = iotServer.getCommandControl()
            if cmdControl:
                cmd = cmdControl["cmd"]
                arg = cmdControl["arg"]

                if cmd == "showMessage":
                    print("showMessage", arg)
                    lcdShow(arg[0])
                    iotServer.pushLEDMessage(arg[0])
                elif cmd == "addNewGuest":
                    print("addNewGuest", arg)
                    iotServer.faceEngine.addNewGuest(arg[0], arg[1])


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()