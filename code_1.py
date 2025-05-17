import os
import time
import ssl
import socketpool
import microcontroller
import board
import busio
import adafruit_requests as requests
import adafruit_connection_manager
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_io.adafruit_io_errors
#import adafruit_ahtx0
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import analogio
import collections
from collections import deque
import time
import re
import storage
import adafruit_dht
import digitalio
from analogio import AnalogIn

analog_in = AnalogIn(board.A1)

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

soil_moisture_level = round(get_voltage(analog_in), 3)
print(soil_moisture_level, "= moisture level")
dhtDevice = adafruit_dht.DHT22(board.GP15) #sensor device                                                                                                                             
temperature_c = dhtDevice.temperature  #gets temperature from sensor device
temperature_f = temperature_c * (9 / 5) + 32  #calculates farenhight from sensor device
humidity = dhtDevice.humidity # gets humidity from sensor device
print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
)             # prints temperature and humidity                                                  


ADAFRUIT_AIO_USERNAME = "CuthbertB"  # adafruit username
ADAFRUIT_AIO_KEY      = ""  #adafruit key

aio_username = "CuthbertB"
aio_key = "aio_oBRJ96vaDyheQ4P0goVvwUluX9dt"
feed_io = "https://io.adafruit.com/api/v2/CuthbertB/feeds/temp2w"

def connected(client, userdata, flags, rc):
    print("Connected to Adafruit IO")

def disconnected(client, userdata, rc):
    print("Disconnected from Adafruit IO")

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
connection_manager = adafruit_connection_manager.get_connection_manager(pool)

mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    port=1883,
    username=aio_username,
    password=aio_key,
    socket_pool=pool,
    ssl_context=ssl_context,
) # sets up mqtt
  
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...") 
mqtt_client.connect()

try:
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print("got wifi password")
except TypeError:
    print("Could not find WiFi info. Check your settings.toml file!")
    raise # connects to wifi

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)
print("connected to io")

try:
# get feed
    feed_temp = aio_username + "/feeds/temp2w"
    feed_humid = aio_username + "/feeds/humid2w"
    feed_soil = aio_username + "/feeds/soil-m"
    print("connected to temp2w")
except AdafruitIO_RequestError:
    print("error")
#    if no feed exists, create one
#    picowTemp_feed = io.create_new_feed("temp2w")
#    picowHumid_feed = io.create_new_feed("humid2w")
#    picowSoil_feed = io.create_new_feed("soil-m")
    
#    picoAverage_feed = io.create_new_feed("AverageTemp")

#  pack feed names into an array for the loop
feed_names = feed_temp
feed_name1 = feed_humid
feed_name2 = feed_soil
#feed_ave = picoAverage_feed
print("feeds created")

clock = 1000

while True:
    try:
        #  when the clock runs out..
        if clock > 300:
            #  read sensor
#            dhtDevice = adafruit_dht.DHT22(board.GP19)
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            soil_moisture_level = round(get_voltage(analog_in), 3)
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
            )
            mqtt_client.connect()       
            mqtt_client.publish(feed_name1, humidity) #poublishes to adafruit feed
            mqtt_client.publish(feed_names, temperature_c)
            mqtt_client.publish(feed_name2, soil_moisture_level)
            soil_moisture_level = round(get_voltage(analog_in), 3)
            print("Sent")
            time.sleep(150)
            #  read sensor
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            soil_moisture_level = round(get_voltage(analog_in), 3)
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
            )
            mqtt_client.connect()
            mqtt_client.publish(feed_names, temperature_c)
            mqtt_client.publish(feed_name1, humidity)
            mqtt_client.publish(feed_name2, soil_moisture_level)
            print("Sent")
            print(soil_moisture_level, "= moisture level")
            time.sleep(150)
        else:
            clock += 600
    # pylint: disable=broad-except
    #  any errors, reset Pico W
    except Exception as e:
            #  read sensor
 #           dhtDevice = adafruit_dht.DHT22(board.GP19)
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            soil_moisture_level = round(get_voltage(analog_in), 3)
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
            )
            mqtt_client.connect()
            mqtt_client.publish(feed_names, temperature_c)
            mqtt_client.publish(feed_name1, humidity)
            mqtt_client.publish(feed_name2, soil_moisture_level)
            print("Sent")
            print((get_voltage(analog_in), "= moisture level"))
            time.sleep(150)
    #  delay
    time.sleep(150)
    print(clock)  
#this code will run and run and run.


