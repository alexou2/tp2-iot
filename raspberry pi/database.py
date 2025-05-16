import sqlite3
import requests
import json
con = sqlite3.connect('example.db')
cur = con.cursor()
firebase_url_sensors = "https://fuck-off-abc63-default-rtdb.firebaseio.com/sensor_readings.json?auth=<4G997bxZerZBnShZCCHGizZYaHt2>"
firebase_url_states = "https://fuck-off-abc63-default-rtdb.firebaseio.com/rpi_state.json"


def init_table():
# Create table
    try:
        cur.execute('''CREATE TABLE data
               (id integer primary key, temp INTEGER, humidity INTEGER, door_open boolean, alarm_on boolean, in_test_mode boolean, is_synced boolean)''')
        con.commit()
        # con.close()
    except Exception as e:
        print("database already created")

def update_local(temp, humidity, door_open, alarm_on,  in_test_mode):
    print(humidity)
    cur.execute("INSERT INTO data VALUES (null, ?, ?, ?, ?, ?, false)", (temp, humidity, door_open, alarm_on,  in_test_mode))
    con.commit()
    # con.close()




def sync_firebase():
    cur.execute('SELECT * FROM data WHERE is_synced=false')
    unsynced = cur.fetchall()

    for data in unsynced:
        print(data[0])
        sen = {
            "id":data[0],
            "temp":data[1],
            "humidity":data[2],
            "door_open":data[3],
            "alarm_on":data[4],
            "in_test_mode": data[5]
        }
        try:
            res = requests.post(firebase_url_sensors, data=json.dumps(sen))
            update = "UPDATE data SET is_synced=? WHERE id=?"
            con.execute(update, (True, data[0]))
            con.commit()
        except Exception as e:
            print("fail")

def get_system_states() :
    try:
        response = requests.get(firebase_url_states)
        system_states = response.json()
        
    except Exception as e:
            print("fail")
            system_states = []
    return system_states