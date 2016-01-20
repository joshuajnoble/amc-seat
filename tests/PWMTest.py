from PWM import PWM
import time

CUPHOLDER_PWM = 12
CUPHOLDER_2_PWM = 13

UNDER_SEAT_PWM = 0
UPPER_SHELL_RED = 8
UPPER_SHELL_GREEN = 9
UPPER_SHELL_BLUE = 10

# Initialise the PWM device using the default address
pwm = PWM(0x42)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x42)


freq = 0
pwm.setPWMFreq(500)                        # Set frequency to 60 Hz
while (True):
	if freq > 4095:
		freq = 0
	else:
		freq = freq + 10	
	
	pwm.setPWM(UNDER_SEAT_PWM, 4095 - freq, freq)
	pwm.setPWM(CUPHOLDER_PWM, 4095 - freq, freq)
	pwm.setPWM(UPPER_SHELL_GREEN, 4095 - freq, freq)
	pwm.setPWM(UPPER_SHELL_BLUE, 4095 - freq, freq)
	pwm.setPWM(UPPER_SHELL_RED, 2048, 2048)
	pwm.setPWM(CUPHOLDER_2_PWM, 4095 - freq, freq)

