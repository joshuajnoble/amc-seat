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
from time import sleep
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect

GPIO.setmode(GPIO.BOARD)

ID = 1

global player #video


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
VIDEO_FILE_1 = "/home/pi/1-seat-number.m4v"

ledDriver = PWM(0x42)

connections = []

############################################################
# gpio
############################################################

PROJECTOR_ON_OFF = 29# gpio5
PROJECTOR_MENU = 31# GPIO6
AUDIO_LED = 22# GPIO25
AUDIO_PLUG_DETECT = 32# GPIO12
SEAT_OCCUPANCY = 15# GPIO22

#PROJECTOR_ON_OFF = 5
#PROJECTOR_MENU = 6
#AUDIO_LED = 25
#AUDIO_PLUG_DETECT = 12
#SEAT_OCCUPANCY = 22

############################################################
# pwm via PCA9685
############################################################

CUPHOLDER_PWM = 12
UNDER_SEAT_PWM = 0
UPPER_SHELL_RED = 8
UPPER_SHELL_GREEN = 9
UPPER_SHELL_BLUE = 10


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

@socketio.on("set_color")
def set_color(message):

	if(message['id'] == ID):
		# huh?
		ledDriver.setPWM(UPPER_SHELL_RED, message['red'], 100 - message['red'])
		ledDriver.setPWM(UPPER_SHELL_GREEN, message['green'], 100 - message['green'])
		ledDriver.setPWM(UPPER_SHELL_BLUE, message['blue'], 100 - message['blue'])

	else:
		#this sends to everyone, let them figure out who needs what
		emit('set_color', message, broadcast=True)

	print message

@socketio.on("show_1")
def show_1(message):

	if(message['id'] == ID):
		if(player):
			player.quit()
		player = OMXPlayer("/home/pi/2-welcome.m4v")

	else:
		#this sends to everyone, let them figure out who needs what
		emit('show_1', message, broadcast=True)

	print message


@socketio.on("show_2")
def show_2(message):

	if(message['id'] == ID):
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
		#lowbyte = proxSensor2.readU8(0x5F)
		#highbyte = proxSensor2.readU8(0x5E)
		#byte2 = (highbyte << 3) | lowbyte

		if byte1 < 200: #anything closer?
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
    print "seat occupied"
    #what happens here?

def audio_plug_insert():
    GPIO.output(AUDIO_LED, GPIO.HIGH);



def start_up():

    

    #player.quit()
    #GPIO.output(PROJECTOR_ON_OFF, GPIO.HIGH)
    #sleep(3.0)
    #GPIO.output(PROJECTOR_ON_OFF, GPIO.LOW)

if __name__ == "__main__":
   
    ledDriver.setPWM(CUPHOLDER_PWM, 4095, 0)
    ledDriver.setPWM(UNDER_SEAT_PWM, 4095, 0)
    ledDriver.setPWM(UPPER_SHELL_RED, 4095, 0)
    ledDriver.setPWM(UPPER_SHELL_GREEN, 4095, 0)
    ledDriver.setPWM(UPPER_SHELL_BLUE, 4095, 0)

    GPIO.setup(PROJECTOR_MENU, GPIO.OUT)
    GPIO.setup(PROJECTOR_ON_OFF, GPIO.OUT)
    GPIO.setup(AUDIO_LED, GPIO.OUT)
    GPIO.setup(AUDIO_PLUG_DETECT, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(SEAT_OCCUPANCY, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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
    
    GPIO.add_event_detect(SEAT_OCCUPANCY, GPIO.FALLING, callback = seat_occupied, bouncetime = 200)
    GPIO.add_event_detect(AUDIO_PLUG_DETECT, GPIO.FALLING, callback = audio_plug_insert, bouncetime = 200)

    global player = OMXPlayer(VIDEO_FILE_1)
    player.play()
    # now what ?
    print "started"
    sleep(1)
    player.pause()

    socketio.run(app, debug=True, host='0.0.0.0')
    threadStart()

    while True:
		lowbyte = proxSensor1.readU8(0x5F)
		highbyte = proxSensor1.readU8(0x5E)
		byte1 = (highbyte << 3) | lowbyte
		#lowbyte = proxSensor2.readU8(0x5F)
		#highbyte = proxSensor2.readU8(0x5E)
		#byte2 = (highbyte << 3) | lowbyte

		if byte1 < 200: #anything closer?
			ledDriver.setPWM(UNDER_SEAT_PWM, 0, 4095)
		else:
			ledDriver.setPWM(UNDER_SEAT_PWM, 4095, 0)

		sleep(0.5)


    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
