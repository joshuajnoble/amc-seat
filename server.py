from flask import Flask
from omxplayer import OMXPlayer
import RPi.GPIO as GPIO
import subprocess

import threading
import atexit
from Adafruit_I2C import Adafruit_I2C
from PWM import PWM

async_mode = None
# monkey patching is necessary because this application uses a background
# thread

import eventlet
eventlet.monkey_patch()

import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect


player = 0

onTime = 50
offTime = 50

########################################################################
# threads
########################################################################

POOL_TIME = 0.05 #Seconds for polling

# this is where the flags coming from the two motion sensors
proximityFlag = 0 
# lock to control access to variable
dataLock = threading.Lock()
# thread handler
i2cThread = threading.Thread()

########################################################################
# i2c
########################################################################

#prox sensor
GP2Y0E02B = 0x40

proxSensor1 = Adafruit_I2C(GP2Y0E02B)

ledDriver = PWM()

connections = []

########################################################################
# sockets
########################################################################

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

@socketio.on_error()
def error_handler(e):
    print e

@socketio.on("connect")
def connect():
    print "connected"

@socketio.on('test')
def test_handler(message):
    print "TEST WORKS"
    print message + ' '  + str(message['data'])

@socketio.on("show_1")
def show_1(message):

	if(message['data'] == '1'):
		if(player):
			player.quit()
		player = OMXPlayer("path/to/file.mp4")

	else:
		#this sends to everyone, let them figure out who needs what
		emit('show_2', message, broadcast=True)

	print message


@socketio.on("show_2")
def show_2(message):

	if(message['data'] == '1'):
		if(player):
			player.quit()
		player = OMXPlayer("path/to/file.mp4")

	else:
		#this sends to everyone, let them figure out who needs what
		emit('show_2', message, broadcast=True)

	print message


@app.route('/ui') #this doesn't work, goes to '/ui/' and 404s
def route_ui():
    return render_template('ui.html');

@app.route('/client')
def static_proxy():
    return "You're a client"


def interrupt():
    global i2cThread
    i2cThread.cancel()

def checkI2C():
    global proximityFlag
    global i2cThread

    with dataLock:
        #set flags for the i2c events detected
		lowbyte = proxSensor1.readU8(0x5F)
		highbyte = proxSensor1.readU8(0x5E)
		byte1 = (highbyte << 3) | lowbyte
		lowbyte = proxSensor2.readU8(0x5F)
		highbyte = proxSensor2.readU8(0x5E)
		byte2 = (highbyte << 3) | lowbyte

		if byte1 < 400: #anything closer?
			proximityFlag[0] = 1


    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()

def threadStart():

    global i2cThread
    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()


########################################################################
# gpio
########################################################################

def seat_occupied():
    #what happens here?

def audio_plug_insert():
    GPIO.output(AUDIO_LED, GPIO.HIGH);



def start_up():

    GPIO.setup(PROJECTOR_MENU, GPIO.OUT)
    GPIO.setup(PROJECTOR_ON_OFF, GPIO.OUT)
    GPIO.setup(AUDIO_LED, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(AUDIO_PLUG_DETECT, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(SEAT_OCCUPANCY, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    #GPIO.add_event_detect(SEAT_OCCUPANCY, GPIO.FALLING, callback = seat_occupied, bouncetime = 200)
    #GPIO.add_event_detect(AUDIO_PLUG_DETECT, GPIO.FALLING, callback = audio_plug_insert, bouncetime = 200)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW)
    GPIO.output(PROJECTOR_ON_OFF, GPIO.HIGH)
    sleep(1.0)
    GPIO.output(PROJECTOR_ON_OFF, GPIO.LOW)
    sleep(25.0)
    # pulse 3 times to select HDMIi
    print "pulse for hdmi"
    GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
    sleep(0.7)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW);
    sleep(0.7)
    GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
    sleep(0.7)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW);
    sleep(0.7)
    GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
    sleep(0.7)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW);
    sleep(3)

    player = OMXPlayer(VIDEO_FILE_1)
    player.play()
    # now what ?
    print "started"
    sleep(5)

    player.quit()
    GPIO.output(PROJECTOR_ON_OFF, GPIO.HIGH)
    sleep(3.0)
    GPIO.output(PROJECTOR_ON_OFF, GPIO.LOW)

if __name__ == "__main__":
    
    socketio.run(app, debug=True, host='0.0.0.0')
    threadStart()

    while 1:
		if( proximityFlag == 1 ): #did we get a trigger
			#turn PWM up
			ledDriver.setPWM(1, led1Timing, led1Timing)
			led1Timing -= 2
			if led1Timing == 0:
				proximityFlag = 0

		sleep(0.1)


    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
