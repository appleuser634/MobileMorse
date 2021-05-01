import RPi.GPIO as GPIO
import time

pin = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin,GPIO.OUT,initial=GPIO.LOW)

p = GPIO.PWM(pin,1)


p.start(50)
p.ChangeFrequency(329)
time.sleep(0.2)
p.stop()

p.start(50)
p.ChangeFrequency(261)
time.sleep(0.2)
p.stop()
time.sleep(0.1)

p.start(50)
p.ChangeFrequency(392)
time.sleep(0.5)
p.stop()
time.sleep(0.5)


p.stop()
GPIO.cleanup()
