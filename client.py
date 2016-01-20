from socketIO_client import SocketIO, LoggingNamespace

import thread
import time

import eventlet
eventlet.monkey_patch()

from Adafruit_I2C import Adafruit_I2C
from PWM import PWM

global player
player = None

global occupied
occupied = False

global firstTrigger
firstTrigger = True

global eventletThread

ID = 2 #what ID am I?

onTime = 50
offTime = 50

############################################################
# gpio
############################################################

PROJECTOR_ON_OFF = 5
PROJECTOR_MENU = 6
AUDIO_LED = 25
AUDIO_PLUG_DETECT = 12
SEAT_OCCUPANCY = 22

############################################################
# pwm via PCA9685
############################################################

CUPHOLDER_PWM = 12
UNDER_SEAT_PWM = 0
UPPER_SHELL_RED = 8
UPPER_SHELL_GREEN = 9
UPPER_SHELL_BLUE = 10

############################################################
# i2c
############################################################

# prox detection address
GP2Y0E02B = 0x40


proxSensor1 = Adafruit_I2C(GP2Y0E02B)
#proxSensor2 = Adafruit_I2C(VCNL4010_I2CADDR_DEFAULT)

#PWM driver connected on i2c
ledDriver = PWM(0x42)

########################################################################
# websocket
########################################################################

amcServerIP = '192.168.42.1'

def on_show_video_1(message):
    if(message['id'] == ID):
    	global player
        if(player):
            player.quit()
        player = OMXPlayer("path/to/file.mp4", args=['--no-osd', '--no-keys', '-b'])

    print message


def on_show_video_2(message):

    if(message['id'] == ID):
    	global player
        if(player):
            player.quit()
        player = OMXPlayer("path/to/file.mp4", args=['--no-osd', '--no-keys', '-b'])
    
    print message

def set_color(message):
    ledDriver.setPWM(UPPER_SHELL_RED, message['red'], 4095 - message['red'])
    ledDriver.setPWM(UPPER_SHELL_GREEN, message['green'], 4095 - message['green'])
    ledDriver.setPWM(UPPER_SHELL_BLUE, message['blue'], 4095 - message['blue'])


def reset_handler():
	emit("reset", "", broadcast=True)
	global firstTrigger
	firstTrigger = True
	global occupied
	occupied = False
	global player
	player = OMXPlayer(VIDEO_FILE_1)
	player.play()
	sleep(1)
	player.pause()
	ledDriver.setPWM(UPPER_SHELL_RED, 0, 4095)
	ledDriver.setPWM(UPPER_SHELL_GREEN, 0, 4095)
	ledDriver.setPWM(UPPER_SHELL_BLUE, 0, 4095) 


########################################################################
# gpio
########################################################################

def seat_occupied(channel):
	global occupied	
	if GPIO.input(SEAT_OCCUPANCY) == True:
		print "not occupied any more"
		occupied = False
		lowbyte = proxSensor1.readU8(0x5F)
		highbyte = proxSensor1.readU8(0x5E)
		byte1 = (highbyte << 3) | lowbyte
		print "non-occupied distance " + str(byte1)
		if byte1 < 300: #anything closer?
			ledDriver.setPWM(UNDER_SEAT_PWM, 0, 4095)
			sleep(10.0)
		else:
			ledDriver.setPWM(UNDER_SEAT_PWM, 4095, 0)

	else:
		global player
		#if player != None:
		if occupied == False:
			occupied = True
			player.play_pause()
			player.quit()
			sleep(0.5)
			player = OMXPlayer(VIDEO_FILE_2, args=['--no-osd', '--no-keys', '-b'])
			player.play()
			sleep(1.0)
			ledDriver.setPWM(CUPHOLDER_PWM, 0, 4095)
			ledDriver.setPWM(CUPHOLDER_2_PWM, 0, 4095)
			sleep(5)
			ledDriver.setPWM(CUPHOLDER_PWM, 4095, 0)
			ledDriver.setPWM(CUPHOLDER_2_PWM, 4095, 0)

def audio_plug_insert():
    GPIO.output(AUDIO_LED, GPIO.HIGH)

def signal_handler(signal, frame):
	global player
	player.quit()
	sys.exit(0)


########################################################################
# i2c
########################################################################


def checkI2C():

	eventlet.sleep(0.2)

    global firstTrigger
    global occupied

	if occupied == True and firstTrigger == True:
    	#set flags for the i2c events detected
		lowbyte = proxSensor1.readU8(0x5F)
		highbyte = proxSensor1.readU8(0x5E)
		byte1 = (highbyte << 3) | lowbyte

		if byte1 < 300: #anything closer?
			ledDriver.setPWM(UNDER_SEAT_PWM, 0, 4095)
			sleep(10.0)
			firstTrigger = False
		else:
			ledDriver.setPWM(UNDER_SEAT_PWM, 4095, 0)

	global eventletThread
	eventletThread = eventlet.spawn(checkI2C)
    eventletThread.wait()


if __name__ == "__main__":
    print "starting up"
    socketIO = SocketIO('192.168.42.1', 5000, LoggingNamespace)
    print socketIO.connected()
    while socketIO.connected() == False:
         print "not connected"
         sleep(2.0)
         socketIO = SocketIO('192.168.42.1', 5000, LoggingNamespace)

   
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
    sleep(1.0)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW);
    sleep(1.0)
    GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
    sleep(1.0)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW);
    sleep(1.0)
    GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
    sleep(1.0)
    GPIO.output(PROJECTOR_MENU, GPIO.LOW);
    sleep(3.0)
    
    GPIO.add_event_detect(SEAT_OCCUPANCY, GPIO.BOTH, callback = seat_occupied, bouncetime = 2000)
    GPIO.add_event_detect(AUDIO_PLUG_DETECT, GPIO.FALLING, callback = audio_plug_insert, bouncetime = 2000)

    global player
    player = OMXPlayer(VIDEO_FILE_1, args=['--no-osd', '--no-keys', '-b'])
    player.play()
    # now what ?
    sleep(1)
    player.pause()

    global eventletThread
	eventletThread = eventlet.spawn(checkI2C)
    eventletThread.wait()