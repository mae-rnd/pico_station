import paho.mqtt.client as mqtt
import pandas as pd
import time
import schedule
from sqlalchemy import create_engine

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = [("TEMPERATURE", 0), ("HUMIDITY", 0), ("PRESSURE", 0), ("CO2", 0), ("TVOC", 0)]
MQTT_USER = "USER"
MQTT_PASSWORD = "PASS"

DATABASE_URI = "mysql+mysqldb://user:pass@127.0.0.1:3306/pico"
engine = create_engine(DATABASE_URI)

data = {}

def on_message(client, userdata, message):
    try:
        payload = message.payload.decode('utf-8')
        topic = message.topic
        print(f"Incoming : {payload} (Topic : {topic})")

        if topic not in data:
            data[topic] = []
        data[topic].append(payload)
    except Exception as e:
        print(f"Error while processing message : {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_message = on_message

def job():
    global data

    try:
         client.connect(MQTT_BROKER, MQTT_PORT)
    except Exception as e:
         print(f"Error connecting to MQTT broker: {e}")
         exit(1)
    client.subscribe(MQTT_TOPICS)

    print("Listening to MQTT broker...")
    client.loop_start()
    time.sleep(6)
    client.loop_stop()
    df = pd.DataFrame.from_dict(data,orient='index').transpose()
    df = df.head(1)
    df['Date'] = time.strftime('%Y-%m-%d %H:%M:%S')
    df.to_sql('mqtt', engine, if_exists='append', index=False)
    data = {}

    client.disconnect()

for i in range(0,24):
    if i<10:
        j = (f'0{i}')
    else:
        j = i    
    schedule.every().day.at(f'{j}:00').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)