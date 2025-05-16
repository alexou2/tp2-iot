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

def change_door_state() :
    global is_door_open
    global in_test_mode
    if is_door_open :
        is_door_open = False
        move_servo(0)
        door_text = "Fermer"
        if in_test_mode :
            open_door_btn['state'] = tk.NORMAL
            close_door_btn['state'] = tk.DISABLED
    else :
        is_door_open = True
        move_servo(1)
        door_text= "Ouvert"
        if in_test_mode :
            open_door_btn['state'] = tk.DISABLED
            close_door_btn['state'] = tk.NORMAL
    state_label.config(text=f"Etat de la porte: {door_text}")


def close_door(event):
    global door_overriden
    change_door_state()
    if in_test_mode:
        door_overriden = True
    
def open_door(event):
    global door_overriden
    change_door_state()
    if in_test_mode:
        door_overriden = True

def check_temp():
    global is_door_open
    global door_overriden
    if current_temp > max_temp :
       if not is_door_open and not door_overriden :
          change_door_state()
       if alarm_is_enabled :
          led.on()
          buzzer.start(1)
    else:
        if is_door_open and not door_overriden:
            change_door_state()
        led.off()
        buzzer.stop()


def increase_temp(event):
    global current_temp
    current_temp +=1
    
def decrease_temp(event):
    global current_temp
    current_temp-=1
    
def diable_all_test_btn() :
    open_door_btn['state'] = tk.DISABLED
    close_door_btn['state'] = tk.DISABLED
    alarm_off['state'] = tk.DISABLED
    alarm_on['state'] = tk.DISABLED
    temp_up['state'] = tk.DISABLED
    temp_down['state'] = tk.DISABLED
    
def enable_some_test_btn() :
    if is_door_open :
        open_door_btn['state'] = tk.DISABLED
        close_door_btn['state'] = tk.NORMAL
    else :
        open_door_btn['state'] = tk.NORMAL
        close_door_btn['state'] = tk.DISABLED
        
    if alarm_is_enabled :
        alarm_on['state'] = tk.DISABLED
        alarm_off['state'] = tk.NORMAL
    else :
        alarm_on['state'] = tk.NORMAL
        alarm_off['state'] = tk.DISABLED
    temp_up['state'] = tk.NORMAL
    temp_down['state'] = tk.NORMAL

def toggle_test_mode(event):
    global in_test_mode
    global door_overriden
    if in_test_mode :
        in_test_mode = False
        diable_all_test_btn()
        text_test_mode = "Desactiver"
        door_overriden = False
    else :
        in_test_mode = True
        enable_some_test_btn()
        text_test_mode = "Activer"
    mode_label.config(text =f"Mode test : {text_test_mode}")

def disable_alarm(event):
    global alarm_is_enabled
    alarm_is_enabled = False
    alarm_off['state'] = tk.DISABLED
    alarm_on['state'] = tk.NORMAL
    
def enable_alarm(event):
    global alarm_is_enabled
    alarm_is_enabled = True
    alarm_off['state'] = tk.NORMAL
    alarm_on['state'] = tk.DISABLED

    

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
            if hum != None:
                current_humidity = hum
            
    except Exception as error:        
        print("err")
        #continue
    temp_value.config(text=f"{current_temp} C")
    humidity_value.config(text=f"{current_humidity} % hum")
    check_temp()
    
    window.after(1000, get_temperature)
    
def update_data():
    db.update_local(current_temp, current_humidity, is_door_open, alarm_is_enabled, in_test_mode)
    db.sync_firebase()
    window.after(15000, update_data)
    

window = tk.Tk()



window.geometry("640x480")

head_label = tk.Label(window, text = "Systeme de surveillance", font=("Arial", 19, "bold"), bd=10)
head_label.pack()

temp_label = tk.Label(window, text="Temperature", font=("Arial", 15, ""), bd=5)
temp_label.pack()



temp_value = tk.Label(window, fg = "red", font=("Arial", 14, "bold"), bd=5)
temp_value.pack()

humidity_value = tk.Label(window, fg = "red", font=("Arial", 14, "bold"), bd=5)
humidity_value.pack()


state_label=tk.Label(window, text=f"Etat de la porte: {door_text}", font=("Arial", 15,""),bd=5)
state_label.pack()

mode_label = tk.Label(window, text=f"Mode test : {text_test_mode}", font=("Arial", 15,""),fg="blue",bd=5) 
mode_label.pack()

mode_button = tk.Button(window, text="Basculer mode test",bd=5)
mode_button.pack()

mode_button.bind("<Button-1>", toggle_test_mode)

temp_label = tk.Label(window, text="Temperature", font=("Arial", 14,""),bd=5)
temp_label.pack()

temp_frame = tk.Frame(window, bd=5)
temp_frame.pack()
temp_down = tk.Button(temp_frame, text="-", bg="red")
temp_up = tk.Button(temp_frame, text="+", bg="green")
temp_down.pack(side="right", )
temp_up.pack(side="left")
temp_down.bind("<Button-1>", decrease_temp)
temp_up.bind("<Button-1>", increase_temp)


temp_label = tk.Label(window, text="Porte", font=("Arial", 14,""))
temp_label.pack()

door_frame = tk.Frame(window, bd=5)
door_frame.pack()
open_door_btn = tk.Button(door_frame, text="ouvrir", bg="green")
close_door_btn = tk.Button(door_frame, text="fermer", bg="red")  


open_door_btn.pack(side="left")
close_door_btn.pack(side="right")
open_door_btn.bind("<Button-1>", open_door)
close_door_btn.bind("<Button-1>", close_door)


temp_label = tk.Label(window, text="Alarme", font=("Arial", 14,"") )
temp_label.pack()

alarm_frame = tk.Frame(window, bd=5)
alarm_frame.pack()
alarm_on = tk.Button(alarm_frame, text="activer", bg="green")
alarm_off = tk.Button(alarm_frame, text="arreter", bg="red")
alarm_on.pack(side="left")
alarm_off.pack(side="right")
alarm_on.bind("<Button-1>", enable_alarm)
alarm_off.bind("<Button-1>", disable_alarm)

diable_all_test_btn()
window.after(100, get_temperature)
window.after(100, update_data)
window.mainloop()


