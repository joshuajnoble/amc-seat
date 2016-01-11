import websocket
import thread
import time

import Adafruit_I2C
import PWM


onTime = 50
offTime = 50

#let's just pretend it's a VCNL4010
VCNL4010_I2CADDR_DEFAULT = 0x13

proxSensor1 = Adafruit_I2C(VCNL4010_I2CADDR_DEFAULT)
proxSensor2 = Adafruit_I2C(VCNL4010_I2CADDR_DEFAULT)

ledDriver = PWM()


amcServerIP = '192.168.0.1'

def on_message(ws, message):
    if( message == "light1" ):
        ledDriver.setPWM(1, onTime, offTime) # params 1,2 are on,off? in millis?

    if( message == "light1" ):
        ledDriver.setPWM(1, onTime, offTime) # params 1,2 are on,off? in millis?

    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):



if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(amcServerIP,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()