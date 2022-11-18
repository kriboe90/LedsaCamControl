import RPi.GPIO as GPIO

class RgbLed:
    def __init__(self, pins):
        self.pins = pins

    def setup(self, frequency):
        GPIO.setmode(GPIO.BOARD)  # use PHYSICAL GPIO Numbering
        GPIO.setup(self.pins, GPIO.OUT)  # set RGBLED pins to OUTPUT mode
        GPIO.output(self.pins, GPIO.HIGH)  # make RGBLED pins output HIGH level
        self.pwmRed = GPIO.PWM(self.pins[0], frequency)
        self.pwmGreen = GPIO.PWM(self.pins[1], frequency)
        self.pwmBlue = GPIO.PWM(self.pins[2], frequency)
        self.pwmRed.start(0)  # set initial Duty Cycle to 0
        self.pwmGreen.start(0)
        self.pwmBlue.start(0)

    def destroy(self):
        self.pwmRed.stop()
        self.pwmGreen.stop()
        self.pwmBlue.stop()
        GPIO.cleanup()

    def setColor(self, r_val, g_val, b_val, invert_pwm=True):
        if invert_pwm == True:
            r_val = 100 - r_val
            g_val = 100 - g_val
            b_val = 100 - b_val
        self.pwmRed.ChangeDutyCycle(r_val)
        self.pwmGreen.ChangeDutyCycle(g_val)
        self.pwmBlue.ChangeDutyCycle(b_val)