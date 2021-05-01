import RPi.GPIO as GPIO
import time
import sys

sw1 = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(sw1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

text = ""
time_1 = None
push_flag = False

print("Waiting push button...")

while True:
    try:
        if GPIO.input(sw1) == 1:
            if push_flag == False:
                push_flag = True
                time_1 = time.time()
        else:
            if push_flag == True:
                p_time = time.time() - time_1
                
                if p_time > 0.2:
                    text += "-"
                else:
                    text += "."
                push_flag = False
        
        print("\r"+text,end="")
                        
    except KeyboardInterrupt:
        GPIO.cleanup() 
        sys.exit()    
