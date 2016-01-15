from socketIO_client import SocketIO, LoggingNamespace
from omxplayer import OMXPlayer
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

import thread
from time import sleep


ID = 2# what ID am I ?

onTime = 50
offTime = 50

VIDEO_FILE_1 = '/opt/vc/src/hello_pi/hello_video/test.h264'

############################################################
#gpio
############################################################

PROJECTOR_ON_OFF = 29# gpio5
PROJECTOR_MENU = 31# GPIO6
AUDIO_LED = 22# GPIO25
AUDIO_PLUG_DETECT = 32# GPIO12
SEAT_OCCUPANCY = 15# GPIO22

############################################################
# pwm via PCA9685
############################################################

CUPHOLDER_PWM = 12
UNDER_SEAT_PWM = 0
UPPER_SHELL_RED = 8
UPPER_SHELL_GREEN = 9
UPPER_SHELL_BLUE = 10

############################################################ 
#i2c
############################################################

# prox detection address
GP2Y0E02B = 0x40


# proxSensor1 = Adafruit_I2C(GP2Y0E02B)# proxSensor2 = Adafruit_I2C(VCNL4010_I2CADDR_DEFAULT)

# ledDriver = PWM()

########################################################################i
# websocket
########################################################################

amcServerIP = '192.168.42.1'

def on_show_video_1(message):

    if (message['data'] == ID):
        if (player):
            player.quit()
        player = OMXPlayer(VIDEO_FILE_1)

    print message


def on_show_video_2(message):

    if (message['data'] == ID):
        if (player):
            player.quit()
        player = OMXPlayer("path/to/file.mp4")

    print message




######################################################################### gpio########################################################################


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
    start_up()
