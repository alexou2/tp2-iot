from gpiozero import LED
from gpiozero import Buzzer
from gpiozero import Servo
from time import sleep
import board
import adafruit_dht
import tkinter as tk
import database as db


db.init_table()

led = LED(2)

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(3,GPIO.OUT)
buzzer = GPIO.PWM(3, 1000)
#buzzer = Buzzer(3)
sensor = adafruit_dht.DHT11(board.D4, use_pulseio=False)


myCorrection=0.45
maxPW=(2.0+myCorrection)/1000
minPW=(1.0-myCorrection)/1000

servo = Servo(5,min_pulse_width=minPW,max_pulse_width=maxPW)

door_text = "Fermer"

max_temp = 25.0
current_temp = 0
current_humidity = 0
alarm_is_enabled = True
is_door_open = False
in_test_mode = False
text_test_mode = "Desactiver"
door_overriden = False

def move_servo(value):
    servo.value = value
    sleep(0.15)
    servo.value = None

move_servo(0)


def override_door_state(override_value) :
    global is_door_open
    global in_test_mode
    global door_overriden
    if in_test_mode :
        door_overriden = True
        is_door_open = override_value
        if is_door_open :
            move_servo(1)
        else :
            move_servo(0)
    



def check_temp():
    global is_door_open
    global door_overriden
    if current_temp > max_temp :
       if not is_door_open and not door_overriden :
          move_servo(1)
          is_door_open = True
       if alarm_is_enabled :
          if not led.is_active :
            led.on()
            buzzer.start(1)
    else:
        if is_door_open and not door_overriden:
            move_servo(0)
            is_door_open = False
        led.off()
        buzzer.stop()
    print(f"Door state{is_door_open}")
    print(f"Alarm state{alarm_is_enabled}")



    
def override_temp(override_temp_value):
    global current_temp
    global in_test_mode
    if in_test_mode :
        current_temp = override_temp_value
    


def change_test_mode_state(override_value) :
    global in_test_mode
    global alarm_is_enabled
    global door_overriden
    in_test_mode = override_value
    if not in_test_mode :
        door_overriden = False
        alarm_is_enabled = True


    
def change_alarm_state(state_alarm_override):
    global alarm_is_enabled
    global in_test_mode
    if in_test_mode :
        alarm_is_enabled = state_alarm_override

    

def get_temperature():
    global current_temp
    global current_humidity
    led.off()
    buzzer.stop()
    #while True:
    
    try: 
        if not in_test_mode:
            temp = sensor.temperature
            hum = sensor.humidity
            if temp != None:
                current_temp = temp 
                print(f"Temp{current_temp}" )
            if hum != None:
                current_humidity = hum
                print(f"Humidity{current_humidity}" )
            
            
    except Exception as error:        
        print("err")
        #continue
    check_temp()
    
def update_data():
    db.update_local(current_temp, current_humidity, is_door_open, alarm_is_enabled, in_test_mode)
    db.sync_firebase()
    

def apply_system_states() :
    system_states = db.get_system_states()
    print(system_states)
    if check_json_not_null(system_states) :  
        try:
            change_test_mode_state(system_states["state_test_mode"])
        except:
            ()
        try:   
            change_alarm_state(system_states["state_alarm"])
        except:
            ()
        try:
            override_door_state(system_states["state_door"])
        except:
            ()
        try:
            override_temp(system_states["state_temp"])
        except:
            () 

def check_json_not_null(data):
    if data is None :
        return False
    for value in data.values():
        if value is None:
            return False
    return True

db.init_table()
while True :
   update_data()
   apply_system_states()
   get_temperature()
   sleep(2)
   
    





