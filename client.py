import RPi.GPIO as GPIO
import time
import os, json
import ibmiotf.application
import ibmiotf.device
import uuid

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)

client = None

organization = "kjmozg"
deviceType = "raspberry-leoniknik-0417"
deviceId = "raspberry-leo-0417"
appId = str(uuid.uuid4())
authMethod = "token"
authToken = "qZG7Jy*)n1OHRJtr3G"

def myCommandCallback(cmd):
    print("Command received: %s" % cmd.command)
    if cmd.command == "light":
        command = cmd.data["command"]
        print(command)
        if command == "on":
            GPIO.output(40, GPIO.HIGH)
        elif command == "off":
            GPIO.output(40, GPIO.LOW)

try:
    deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
    client = ibmiotf.device.Client(deviceOptions)
    client.connect()
    client.commandCallback = myCommandCallback

    while True:
       myData = {'buttonPushed' : 1}
       client.publishEvent("input", "json", myData)
       time.sleep(2)

except ibmiotf.ConnectionException  as e:
    print(e)

