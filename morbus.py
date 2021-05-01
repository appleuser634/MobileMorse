import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time
import RPi.GPIO as GPIO
import time
import sys
import boot_display
import requests
import threading
import json
import logging
import pathlib
import datetime

# make log file
log_path = './log/' + str(datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S")) + '.log'
log_file = pathlib.Path(log_path)
log_file.touch()
logging.basicConfig(filename=log_path, level=logging.DEBUG)

# message_config.json
with open('message_config.json', 'r') as json_open:
    json_load = json.load(json_open)

    TO = str(json_load['TO'])
    FROM = str(json_load['FROM'])
    MESSAGE_API_IP = str(json_load['MESSAGE_API_IP'])
    LINE_TOKEN = str(json_load['LINE_TOKEN'])

# set gpio
sw1 = 5
sw2 = 27
sw3 = 13
beep_pin = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(sw1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(beep_pin,GPIO.OUT,initial=GPIO.LOW)

# set oled display
oled_reset = digitalio.DigitalInOut(board.D4)

WIDTH = 128
HEIGHT = 32
BORDER = 5

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

oled.fill(0)
oled.show()

notif_flag = False

def send_message(message,service):
        
    logging.debug('called' + str(sys._getframe().f_code.co_name) + 'function')
    
    if service == "LINE":
        url = "https://notify-api.line.me/api/notify"
        access_token = LINE_TOKEN
        headers = {'Authorization': 'Bearer ' + access_token}

        payload = {'message': message}
        r = requests.post(url, headers=headers, params=payload,)
    
    elif service == "SEND":
        post_url = 'http://'+MESSAGE_API_IP+':4000/messages'
        
        item_data = {
            'message':{
            'who': TO,
            'message': message,
            }
        }

        try:
            r_post = requests.post(post_url, json=item_data)
        except:
            logging.debug("OFFLINE ERROR!!")

    logging.debug("SEND MESSAGE:"+str(message))

    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/IconBitOne.ttf',10)
    
    for i in range(-5,135,5):    

        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        draw.text((i,13), "GW ", font=font, fill=255)

        oled.image(image)
        oled.show()

    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def receive_message():
    
    logging.debug('callse' + str(sys._getframe().f_code.co_name) + 'function')

    get_url = "http://"+MESSAGE_API_IP+":4000/messages"
    try:
        r_get = requests.get(get_url)
        r_get.raise_for_status() # 
        logging.debug(r_get.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Error: ",e)
        return
    
    message_json = r_get.json()["data"]
    message_json = message_json[-10:]
    message_list = [m["message"] for m in message_json if m["who"] == FROM]

    with open("/home/pi/MorBus/message.txt", 'a') as f:
        for m in message_list:
            print(m, file=f)
    
    display_list = []
    with open("/home/pi/MorBus/message.txt", 'r') as f:
        messages = f.read()
        message_list = messages.split("\n")
        message_list.remove("")

        for i,m in enumerate(reversed(message_list)):
            display_text = str(i)+":"+m
            display_list.append(display_text)

    font = ImageFont.truetype('/home/pi/MorBus/fonts/FreePixel.ttf',16)
    font2 = ImageFont.truetype('/home/pi/MorBus/fonts/3Dventure.ttf',16)

    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    chose_index = 0
    start_point = 2

    push_flag = False
    while True:    
        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        
        i = start_point
        for c,mode in enumerate(display_list):
            draw = ImageDraw.Draw(image)
            if c == chose_index: 
                draw.text((2,i), mode, font=font2, fill=255)
            else:
                draw.text((2,i), mode, font=font, fill=255)
            i += 16

        if GPIO.input(sw3) == 1 and push_flag == False:
            logging.debug("PUSH! 3")
            chose_index += 1
            push_flag = True
        
        elif GPIO.input(sw2) == 1 and push_flag == False:
            logging.debug("PUSH! 2")
            return
        else:
            push_flag = False
        
        if chose_index == 2:
            start_point = -14
        
        if chose_index >= len(display_list):
            start_point = 2
            chose_index = 0

        oled.image(image)
        oled.show()
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def recv_animation():
    global notif_flag
    
    logging.debug('called' + str(sys._getframe().f_code.co_name) + 'function')
    
    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/pixel_invaders/pixel_invaders.ttf',16)
    font2 = ImageFont.truetype('/home/pi/MorBus/fonts/Forma.ttf',32)
    font3 = ImageFont.truetype('/home/pi/MorBus/fonts/IconBitOne.ttf',10)
    
    for i in range(-5,53,5):    

        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        draw.text((i,5), "H", font=font, fill=255)

        oled.image(image)
        oled.show()
    
    time.sleep(0.7)
    draw.text((50,15), "A", font=font2, fill=255)
    
    oled.image(image)
    oled.show()
    time.sleep(1)
    
    for i in range(58,135,5):    

        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        draw.text((i,5), "H", font=font, fill=255)
        draw.text((54,20), "W ", font=font3, fill=255)

        oled.image(image)
        oled.show()
    
    notif_flag = False
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')


def notify_thread(message_len):
    global notif_flag

    logging.debug('called' + str(sys._getframe().f_code.co_name) + 'function')
    
    get_url = "http://"+MESSAGE_API_IP+":4000/messages"
    message_id = 0 
    while True:    
        try:
            r_get = requests.get(get_url)
            r_get.raise_for_status()  
            logging.debug(r_get.status_code)
        except requests.exceptions.RequestException as e:
            logging.error("Error: ",e)

        message_json = r_get.json()
        message_list = message_json["data"]

        message_list = [m for m in message_list if m["who"] == FROM]
        
        logging.debug(message_list)
        
        # TODO message_listのlengthの差で未読件数を取得できるので実装する
        if len(message_list) != message_len:
            beep_sound()
            notif_flag = True
            message_id = message_list[-1]["id"]
            message_len = len(message_list)
        
        time.sleep(2)

    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def beep_sound():
    
    logging.debug('called' + str(sys._getframe().f_code.co_name) + 'function')
    
    p = GPIO.PWM(beep_pin,1)

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
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def init_message():
    
    logging.debug('called' + str(sys._getframe().f_code.co_name) + 'function')
    

    get_url = "http://"+MESSAGE_API_IP+":4000/messages"
    
    try:
        r_get = requests.get(get_url)
        r_get.raise_for_status()  
        logging.debug(r_get.status_code)
    except requests.exceptions.RequestException as e:
        logging.error("Error: ",e)
        return 0

    message_json = r_get.json()
    message_list = message_json["data"]
    
    message_list = [m["message"] for m in message_list if m["who"] == FROM]
    
    with open('./message.txt', 'w') as f:
        for m in message_list:
            f.write(str(m)+'\n')

    logging.debug(message_list)
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

    return len(message_list)    

def start_mode(mode_name):
    
    logging.debug('called' + str(sys._getframe().f_code.co_name) + 'function')
    
    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/3Dventure.ttf',16)
     
    for i in range(-5,40,2):

        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0) 

        draw.text((2,i),mode_name, font=font, fill=255)

        oled.image(image)
        oled.show()
        
        if i == 13:
            time.sleep(0.5)
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def cheat_sheet():
    
    logging.debug('start' + str(sys._getframe().f_code.co_name) + 'function')
    
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/Animal-Crossing-Wild-World.ttf',16)
    
    cheat_list = "A .-  B -...  C -.-.  D -..  E .  F ..-.  G --.  H ....  I ..  J .---  K -.-  L .-..  M --  N -.  O ---  P .--.  Q --.-  R .-.  S ...  T -  U ..-  V ...-  W .--  X -..-  Y -.--  Z --.. ! ....-. ? ..--.. ( -.--. ) -.--.- : ---..."

    
    for i in reversed(range(-650,130,3)):    

        if GPIO.input(sw1) == 1:
            logging.debug("PUSH SW1!!")
            return
        
        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        draw.text((i,13), cheat_list, font=font, fill=255)

        oled.image(image)
        oled.show()
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def practice_mode():
        
    logging.debug('start' + str(sys._getframe().f_code.co_name) + 'function')
    
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/Animal-Crossing-Wild-World.ttf',16)
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')


def message_menu():
    global notif_flag

    logging.debug('start' + str(sys._getframe().f_code.co_name) + 'function')

    while GPIO.input(sw1) == 1:
        pass
         
    mode_list = ["SEND","RECEIVE"]
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/FreePixel.ttf',16)
    font2 = ImageFont.truetype('/home/pi/MorBus/fonts/3Dventure.ttf',16)

    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    chose_index = 0
    start_point = 2

    push_flag = False
    while True:
        
        if notif_flag == True:    
            recv_animation()

        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        
        i = start_point
        for c,mode in enumerate(mode_list):
            draw = ImageDraw.Draw(image)
            if c == chose_index: 
                draw.text((2,i), mode, font=font2, fill=255)
            else:
                draw.text((2,i), mode, font=font, fill=255)
            i += 16

        if GPIO.input(sw1) == 1 and push_flag == False:
            logging.debug("PUSH! 1")
            logging.debug("mode:"+str(mode))
            if mode_list[chose_index] == "SEND":
                logging.debug("START SEND!")
                start_mode("SEND")
                morse_type("SEND")
            elif mode_list[chose_index] == "RECEIVE":
                logging.debug("START RECEIVE!")
                start_mode("RECEIVE")
                receive_message()

            push_flag = True

        elif GPIO.input(sw3) == 1 and push_flag == False:
            logging.debug("PUSH! 3")
            chose_index += 1
            push_flag = True
        
        elif GPIO.input(sw2) == 1 and push_flag == False:
            logging.debug("PUSH! 2")
            return
        else:
            push_flag = False

        if chose_index == 2:
            start_point = -14
        
        if chose_index >= len(mode_list):
            start_point = 2
            chose_index = 0

        oled.image(image)
        oled.show()
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def mode_menu():
    global notif_flag

    logging.debug('start' + str(sys._getframe().f_code.co_name) + 'function')
    
    mode_list = ["MESSAGE","LINE","PRACTICE"]
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/FreePixel.ttf',16)
    font2 = ImageFont.truetype('/home/pi/MorBus/fonts/3Dventure.ttf',16)

    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    
    chose_index = 0
    start_point = 2

    push_flag = False
    while True:    
        if notif_flag == True:
            recv_animation()
        
        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        
        i = start_point
        for c,mode in enumerate(mode_list):
            draw = ImageDraw.Draw(image)
            if c == chose_index: 
                draw.text((2,i), mode, font=font2, fill=255)
            else:
                draw.text((2,i), mode, font=font, fill=255)
            i += 16

        if GPIO.input(sw1) == 1 and push_flag == False:
            logging.debug("PUSH! 1")
            logging.debug("mode:"+str(mode))
            if mode_list[chose_index] == "LINE":
                logging.debug("START LINE!")
                start_mode("LINEMODE")
                morse_type("LINE")
            elif mode_list[chose_index] == "MESSAGE":
                logging.debug("START MESSAGE!")
                message_menu()
            elif mode_list[chose_index] == "PRACTICE":
                logging.debug("START PRACTICE!")
                start_mode("PRACTICE!")
            push_flag = True

        elif GPIO.input(sw3) == 1 and push_flag == False:
            logging.debug("PUSH! 3")
            chose_index += 1
            push_flag = True
        else:
            push_flag = False

        if chose_index == 2:
            start_point = -14
        
        if chose_index >= len(mode_list):
            start_point = 2
            chose_index = 0

        oled.image(image)
        oled.show()
    
    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

def morse_type(service):
    
    logging.debug('start' + str(sys._getframe().f_code.co_name) + 'function')
    
    font = ImageFont.truetype('/home/pi/MorBus/fonts/FreePixel.ttf',16)
    font2 = ImageFont.truetype('/home/pi/MorBus/fonts/sonic2.ttf',16)
    
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    morse_list = {"._":"A","_...":"B","_._.":"C","_..":"D",".":"E",".._.":"F",\
                "__.":"G","....":"H","..":"I",".___":"J","_._":"K","._..":"L",\
                "__":"M","_.":"N","___":"O",".__.":"P","__._":"Q","._.":"R",\
                "...":"S","_":"T",".._":"U","..._":"V",".__":"W","_.._":"X",\
                "_.__":"Y","__..":"Z","...._.":"!","......":"?","_.....":"(",\
                "__....":")","___...":":",".____":"1","..___":"2","...__":"3",\
                "...._":"4",".....":"5","_....":"6","__...":"7","___..":"8",\
                "____.":"9","_____":"0","____":"del","...._.":"!","..__..":"?","_.__.":"(","_.__._":")","___...":":"}

    text = ""
    message = ""
    time_1 = None
    push_flag = False
    timeout_flag = False
    time_out = time.time()
    message2 = ""
    kersol_time = time.time()
    
    sw2_flag = False
    sw2_time = None
    
    kersol_flag = False
    kersol_time = time.time()

    while True:    
        draw.rectangle((0,0,WIDTH,HEIGHT), outline=0, fill=0)
        try:
            if GPIO.input(sw3) == 1:
                logging.debug("PUSH SW3!!")
                send_message(message,service)
                message = ""
                text = ""
            
            if GPIO.input(sw2) == 1 and sw2_flag == False:
                logging.debug("PUSH SW2!!")
                sw2_flag = True
                sw2_time = time.time()
                #cheat_sheet()
                #mode_menu()

            if GPIO.input(sw2) != 1 and sw2_flag == True:
                logging.debug("Push time:"+str(time.time() - sw2_time))
                if time.time() - sw2_time > 1.5:
                    cheat_sheet()
                    sw2_flag = False
                    sw2_time = None
                    
                else:
                    mode_menu()
                     
            if sw2_flag == True and time.time() - sw2_time > 1:
                cheat_sheet()
                sw2_flag = False
                sw2_time = None
            
            if GPIO.input(sw1) == 1:
                if push_flag == False:
                    push_flag = True
                    time_out = time.time()
                    timeout_flag = True
                    time_1 = time.time()
            else:
                if push_flag == True:
                    p_time = time.time() - time_1
                    
                    if p_time > 0.25:
                        text += "_"
                    else:
                        text += "."
                    push_flag = False
                    time_out = time.time()
                    timeout_flag = True
            
            try: 
                if time.time() - time_out > 1 and timeout_flag == True:
                    cp_text = text
                    if cp_text == "____":
                        message = message[:-1]
                        timeout_flag = False
                        logging.debug("TEXT:"+str(cp_text))
                        text = ""
                        logging.debug("Message:"+str(message))
                        continue

                    logging.debug("Text:"+str(text))
                    text = ""
                    timeout_flag = False
                    message += morse_list[cp_text]
                    logging.debug("Message:"+str(message))

            except KeyError:
                pass

            oled.fill(0)
            
            # Draw Some Text
            font_width, font_height = font.getsize(text) 
            
            #カーソルの点滅サイクルの管理
            if time.time() - kersol_time > 0.5:
                if kersol_flag == False:
                    kersol_flag = True
                else:
                    kersol_flag = False

                kersol_time = time.time()        

             
            if len(message) >= 16:
                logging.debug("RETURN!!")
                message2 = message[16:]
                logging.debug("MESSAGE:"+str(message))
                logging.debug("MESSAGE2:"+str(message2))
                draw.text((2,2), message[:16], font=font, fill=255)
                draw.text((2,18), message2, font=font, fill=255)
                if kersol_flag == True:
                    draw.text((2+(8*len(message2)),16), "I", font=font2, fill=255)
                
            else:
                draw.text((2,2), message, font=font, fill=255)
                if kersol_flag == True:
                    draw.text((2+(8*len(message)),0), "I", font=font2, fill=255)

            # Display image
            oled.image(image)
            oled.show()

        except KeyboardInterrupt:
            oled.fill(0)
            oled.show()
            GPIO.cleanup() 
            logging.debug("Bye!")
            sys.exit()

    logging.debug('end' + str(sys._getframe().f_code.co_name) + 'function')

if __name__ == "__main__":
    #起動画面を表示
    boot_display.main()
    #メッセージファイルを初期化
    message_len = init_message()
    noti_thread = threading.Thread(target=notify_thread,args=([message_len]))
    noti_thread.start()
    mode_menu()
    morse_line()
