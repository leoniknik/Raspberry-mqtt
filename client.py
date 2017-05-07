import RPi.GPIO as GPIO
import time
import os, json
import ibmiotf.application
import ibmiotf.device
import uuid
from lib_nrf24 import NRF24
import spidev

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

##### NRF
pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

broadcast = 40
pool_arduino = []

radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(0, 17)

radio.setPayloadSize(32)
radio.setChannel(broadcast)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.printDetails()

def NRF_check_pool():
    if len(pool_arduino) == 3:
        return False
    else:
        return True

def NRF_get_channel():
    return 30

def NRF_offer(channel):
    print("NRF_OFFER: " + str(channel))
    message = []
    message.append(channel)
    while len(message) < 32:
        message.append(0)
    print(message)
    radio.write(message)

def NRF_ack():
    message = list("NRF_ACK")
    while len(message) < 32:
        message.append(0)
    print(message)
    radio.write(message)

def NRF_request(channel):
    radio.setChannel(channel)
    start = time.time()
    radio.startListening()

    while not radio.available(0):
        time.sleep(1 / 100)
        if time.time() - start > 5:
            print("Timed out request")
            return

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    print("Received: {}".format(receivedMessage))

    string = ""
    for n in receivedMessage:
        if (n >= 32 and n <= 126):
            string += chr(n)
    print(string)
    if string == "NRF_REQUEST":
        radio.stopListening
        pool_arduino.append(channel)
        NRF_ack()
    radio.stopListening()

def NRF_broadcast():
    radio.setChannel(broadcast)
    start = time.time()
    radio.startListening()

    while not radio.available(0):
        time.sleep(1 / 100)
        if time.time() - start > 2:
            print("Timed out broadcast")
            return

    receivedMessage = []
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
    print("Received: {}".format(receivedMessage))

    string = ""
    for n in receivedMessage:
        if (n >= 32 and n <= 126):
            string += chr(n)
    print(string)
    if string == "NRF_DISCOVER":
        if NRF_check_pool():
            new_channel = NRF_get_channel()
            radio.stopListening()
            NRF_offer(new_channel)
            NRF_request(new_channel)
    radio.stopListening()

def NRF_receive():
    for channel in pool_arduino:
        radio.setChannel(channel)
        radio.startListening()
        start = time.time()
        while not radio.available(0):
            time.sleep(1 / 100)
            if time.time() - start > 3:
                print("Timed out channel " + str(channel))
                return
        receivedMessage = []
        radio.read(receivedMessage, radio.getDynamicPayloadSize())
        print("Received: {}".format(receivedMessage))
        return receivedMessage
##### NRFEND

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

try:
    deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
    client = ibmiotf.device.Client(deviceOptions)
    client.connect()
    client.commandCallback = myCommandCallback

    while True:
        NRF_broadcast()
        print(pool_arduino)
        NRF_data = NRF_receive()
        if NRF_data is not None:
            myData = {'tempreture' : NRF_data[1], 'smoke': NRF_data[0], 'humidity': NRF_data[2]}
            client.publishEvent("input", "json", myData)

except ibmiotf.ConnectionException  as e:
    print(e)

