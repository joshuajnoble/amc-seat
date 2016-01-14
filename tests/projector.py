from socketIO_client import SocketIO, LoggingNamespace

import thread
import time

from Adafruit_I2C import Adafruit_I2C
from PWM import PWM


ID = 2 #what ID am I?

onTime = 50
offTime = 50

VIDEO_FILE_1 = '/opt/vc/src/hello_pi/hello_video/test.h264'

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

ledDriver = PWM()

def interrupt():
  global i2cThread
  i2cThread.cancel()

def checkI2C():
    global commonDataStruct
    global i2cThread

    with dataLock:
        """
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
        """


    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()

def threadStart():

    global i2cThread
    i2cThread  = threading.Timer(POOL_TIME, checkI2C, ())
    i2cThread.start()



########################################################################
# websocket
########################################################################

amcServerIP = '192.168.42.1'

def on_show_video_1(message):

  if(message['data'] == ID):
    if(player):
      player.quit()
    player = OMXPlayer(VIDEO_FILE_1)

  print message


def on_show_video_2(message):

  if(message['data'] == ID):
    if(player):
      player.quit()
    player = OMXPlayer("path/to/file.mp4")

  print message



########################################################################
# gpio
########################################################################

def seat_occupied():
  #what happens here?

def audio_plug_insert():
  GPIO.output(AUDIO_LED, GPIO.HIGH);



def start_up():

  GPIO.setup(PROJECTOR_MENU, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(PROJECTOR_ON_OFF, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(AUDIO_LED, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(AUDIO_PLUG_DETECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(SEAT_OCCUPANCY, GPIO.IN, pull_up_down=GPIO.PUD_UP)

  GPIO.add_event_detect(SEAT_OCCUPANCY, GPIO.FALLING, callback=seat_occupied, bouncetime=200)
  GPIO.add_event_detect(AUDIO_PLUG_DETECT, GPIO.FALLING, callback=audio_plug_insert, bouncetime=200)

  GPIO.output(PROJECTOR_ON_OFF, GPIO.HIGH);
  sleep(10.0)
  #pulse 3 times to select HDMI
  GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
  sleep(0.5)
  GPIO.output(PROJECTOR_MENU, GPIO.LOW);
  sleep(0.5)
  GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
  sleep(0.5)
  GPIO.output(PROJECTOR_MENU, GPIO.LOW);
  sleep(0.5)
  GPIO.output(PROJECTOR_MENU, GPIO.HIGH);
  sleep(0.5)
  GPIO.output(PROJECTOR_MENU, GPIO.LOW);
  sleep(3)

  player = OMXPlayer(VIDEO_FILE_1)

  #now what?
  print "started"



if __name__ == "__main__":
	startup()
