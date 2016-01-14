
from Adafruit_I2C import Adafruit_I2C
import time
from threading import Thread

# this is where the flags coming from the two motion sensors
commonDataStruct = {}

#Seconds for polling
POOL_TIME = 0.5

#prox sensor
GP2Y0E02B = 0x40

proxSensor1 = Adafruit_I2C(GP2Y0E02B)

def interrupt():
    global i2cThread
    i2cThread.cancel()

def checkI2C():
    global commonDataStruct
    global i2cThread

    with dataLock:
        #set flags for the i2c events detected
        lowbyte = proxSensor1.readU8(0x5F)
        highbyte = proxSensor1.readU8(0x5E)
        byte1 = (highbyte << 3) | lowbyte
        print lowbyte
        print highbyte
        print byte1

        if byte1 < 100: #no idea yet
            commonDataStruct[0] = 1

        if byte2 < 100:
            commonDataStruct[1] = 1


    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()

def threadStart():

    global i2cThread
    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()

if __name__ == "__main__":
    threadStart()
    atexit.register(interrupt)