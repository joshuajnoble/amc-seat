from socketIO_client import SocketIO, LoggingNamespace

import thread
import time

from Adafruit_I2C import Adafruit_I2C
from PWM import PWM


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

ledDriver = PWM(0x42)

########################################################################
# websocket
########################################################################

amcServerIP = '192.168.42.1'

def on_show_video_1(message):
    if(message['id'] == ID):
        if(player):
            player.quit()
        player = OMXPlayer("path/to/file.mp4")

    print message


def on_show_video_2(message):

    if(message['id'] == ID):
        if(player):
            player.quit()
        player = OMXPlayer("path/to/file.mp4")
    
    print message

def set_color(message):

    if(message['id'] == ID):
        ledDriver.setPWM(UPPER_SHELL_RED, message['red'], 4095 - message['red'])
        ledDriver.setPWM(UPPER_SHELL_GREEN, message['green'], 4095 - message['green'])
        ledDriver.setPWM(UPPER_SHELL_BLUE, message['blue'], 4095 - message['blue'])

    else:
		#this sends to everyone, let them figure out who needs what
        emit('set_color', message, broadcast=True)

    print message



########################################################################
# gpio
########################################################################

def seat_occupied():
    print "seat occupied"

def audio_plug_insert():
    GPIO.output(AUDIO_LED, GPIO.HIGH)



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

    global player
    player = OMXPlayer(VIDEO_FILE_1)
    player.play()
    # now what ?
    print "started"
    sleep(1)
    player.pause()

    #threadStart()

    while True:
		lowbyte = proxSensor1.readU8(0x5F)
		highbyte = proxSensor1.readU8(0x5E)
		byte1 = (highbyte << 3) | lowbyte
		#lowbyte = proxSensor2.readU8(0x5F)
		#highbyte = proxSensor2.readU8(0x5E)
		#byte2 = (highbyte << 3) | lowbyte

		if byte1 < 100: #anything closer?
			ledDriver.setPWM(UNDER_SEAT_PWM, 0, 4095)
		else:
			ledDriver.setPWM(UNDER_SEAT_PWM, 4095, 0)

		sleep(0.5)


	player.quit()