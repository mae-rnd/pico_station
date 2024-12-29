from machine import Pin, I2C, SoftI2C
import time
import bme280
from umqtt.simple import MQTTClient
import network
import socket
import sgp30

#Light on
led = Pin("LED", Pin.OUT)
led.off()
led.on()

#Connecting to the network
ssid = 'ssid'
password = 'key'
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    print(wlan.ifconfig())
connect()

# BME280 (SoftI2C) & SGP30 configuration (I2C)
si2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=100000)
i2c = I2C(0,sda=Pin(20), scl=Pin(21), freq=100000)

#Connecting to MQTT broker
mqtt_host = "ip address"
mqtt_port = 1883
mqtt_username = "user"
mqtt_password = "pass"
mqtt_client_id = "Pico"

mqtt_client = MQTTClient(
        client_id=mqtt_client_id,
        server=mqtt_host,
        port=mqtt_port,
        user=mqtt_username,
        password=mqtt_password)

mqtt_client.connect()

#Retrieving data from both captors
sgp30 = sgp30.SGP30(i2c=i2c)
sensor = bme280.BME280(i2c=si2c, address=0x77)
while True:
    temperature, pressure, humidity = sensor.values
    air_quality = sgp30.iaq_measure()
    
    print("Température :", temperature)
    print("Pression :", pressure)
    print("Humidité :", humidity)
    print("CO2 : ", air_quality[0])
    print("TVOC : ", air_quality[1])
    print("----------------------")

    mqtt_client.publish("TEMPERATURE", str(temperature))
    mqtt_client.publish("PRESSURE", str(pressure))
    mqtt_client.publish("HUMIDITY", str(humidity))
    mqtt_client.publish("CO2", str(air_quality[0]))
    mqtt_client.publish("TVOC", str(air_quality[1]))
    
    time.sleep(5)
