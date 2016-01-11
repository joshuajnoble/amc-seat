from flask import Flask

import RPi.GPIO as GPIO
import subprocess

import threading
import atexit
import Adafruit_I2C
import PWM

from flask_sockets import Sockets #get us some websocket goodness

playProcess

onTime = 50
offTime = 50

########################################################################
# threads
########################################################################

POOL_TIME = 0.05 #Seconds for polling

# this is where the flags coming from the two motion sensors
commonDataStruct = {}
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
i2cThread = threading.Thread()

########################################################################
# i2c
########################################################################

#let's just pretend it's a VCNL4010
VCNL4010_I2CADDR_DEFAULT = 0x13

proxSensor1 = Adafruit_I2C(VCNL4010_I2CADDR_DEFAULT)
proxSensor2 = Adafruit_I2C(VCNL4010_I2CADDR_DEFAULT)

ledDriver = PWM()


########################################################################
# sockets
########################################################################

app = Flask(__name__)
socketio = SocketIO(app)

def on_message(ws, message):



    if( message == "light1" ):
        ledDriver.setPWM(1, onTime, offTime) # params 1,2 are on,off? in millis?

    if( message == "light2" ):
        ledDriver.setPWM(2, onTime, offTime) # params 1,2 are on,off? in millis?

    if( message == "show_1"):
        playProcess=subprocess.Popen(['omxplayer','-b','Desktop/videos/loop/loop.mp4'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)

    if( message == "show_2"):
        playProcess=subprocess.Popen(['omxplayer','-b','Desktop/videos/loop/loop.mp4'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)

    if( message == "show_3"):
        playProcess=subprocess.Popen(['omxplayer','-b','Desktop/videos/loop/loop.mp4'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)

    print message

# set up the routes for the app, needs static file serving
@app.route("/")
def hello():
    return "You're a client"

@app.route("/ui")
def hello():
    return "This is the UI"

def interrupt():
    global i2cThread
    i2cThread.cancel()

def checkI2C():
    global commonDataStruct
    global i2cThread

    with dataLock:
        #set flags for the i2c events detected

    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()

def threadStart():

    global i2cThread
    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
    threadStart()

    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)