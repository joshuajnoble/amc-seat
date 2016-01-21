import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
SEAT_OCCUPANCY = 15# GPIO22
GPIO.setup(SEAT_OCCUPANCY, GPIO.IN, pull_up_down = GPIO.PUD_UP)

while True:
	print GPIO.input(SEAT_OCCUPANCY)
	sleep(0.2)
