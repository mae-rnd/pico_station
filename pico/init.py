from machine import Pin, I2C
import sgp30

i2c = I2C(0,sda=Pin(20), scl=Pin(21), freq=100000)

sgp30 = sgp30.SGP30(i2c=i2c)

sgp30.iaq_init()
