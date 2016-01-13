from flask import Flask
from omxplayer import OMXPlayer
import RPi.GPIO as GPIO
import subprocess

import threading
import atexit
import Adafruit_I2C
import PWM

from flask.ext.socketio  import SocketIO, emit #get us some websocket goodness

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

connections = []

########################################################################
# sockets
########################################################################

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on("show_1")
def on_message(message):

	if(message['data'] == '1'):
		if(player):
			player.quit()
		player = OMXPlayer("path/to/file.mp4")
	
	else:
		#this sends to everyone, let them figure out who needs what
		emit('show_2', message, broadcast=True)

	print message


@socketio.on("show_2")
def on_message(message):

	if(message['data'] == '1'):
		if(player):
			player.quit()
		player = OMXPlayer("path/to/file.mp4")
	
	else:
		#this sends to everyone, let them figure out who needs what
		emit('show_2', message, broadcast=True)

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
		lowbyte = proxSensor1.readU8(0x5F)
		highbyte = proxSensor1.readU8(0x5E)
		byte1 = (highbyte << 3) | lowbyte
		lowbyte = proxSensor2.readU8(0x5F)
		highbyte = proxSensor2.readU8(0x5E)
		byte2 = (highbyte << 3) | lowbyte
		
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
    app.run(debug=True, host='0.0.0.0')
    threadStart()


    while 1:
		if( commonDataStruct[0] == 1 ): #did we get a trigger
			#turn PWM up
			ledDriver.setPWM(1, led1Timing, led1Timing)
			led1Timing -= 2
			if led1Timing == 0:
				commonDataStruct[0] = 0


		if( commonDataStruct[1] == 1 ): #did we get a trigger
			#turn PWM up
			ledDriver.setPWM(2, led2Timing, led2Timing)
			led2Timing -= 2
			if led2Timing == 0:
				commonDataStruct[1] = 0


		sleep(0.1)

		





    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
