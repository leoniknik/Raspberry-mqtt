import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

GPIO.setmode(GPIO.BCM)

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

while True:
    NRF_broadcast()
    time.sleep(1)
    print(pool_arduino)
    NRF_receive()
