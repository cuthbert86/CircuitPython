# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT

import os
import time
import ssl
import wifi
import socketpool
import microcontroller
import board
import busio
import adafruit_requests as requests
import adafruit_connection_manager
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
#import adafruit_ahtx0
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
import analogio
import microcontroller

t0 = microcontroller.cpu.temperature
print(t0)


aio_username = "myusername"
aio_key = os.getenv("ket from adafruit feed")



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
)

mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()

try:
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
except TypeError:
    print("Could not find WiFi info. Check your settings.toml file!")
    raise

#aio_username = "myusername"
#aio_key = os.getenv("ket from adafruit feed")

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)
print("connected to io")

#  use Pico W's GP0 for SDA and GP1 for SCL
#i2c = busio.I2C(board.GP1, board.GP0)
#aht20 = adafruit_ahtx0.AHTx0(i2c)

try:
# get feed
    picowTemp_feed = aio_username + "/feeds/temperature"
#    picowTemp_feed = io.get_feed("temperature")
    print("connected to temperature")
#    picowHumid_feed = io.get_feed("pihumid")
except AdafruitIO_RequestError:
# if no feed exists, create one
    picowTemp_feed = io.create_new_feed("pitemp")
#    picowHumid_feed = io.create_new_feed("pihumid")

#  pack feed names into an array for the loop
feed_names = picowTemp_feed
print("feeds created")

clock = 300

while True:
    try:
        #  when the clock runs out..
        if clock > 300:
            #  read sensor
            data = microcontroller.cpu.temperature
            mqtt_client.publish(feed_names, data)
            print("Sent")
            time.sleep(5)
            #  print sensor data to the REPL
#            print("\nTemperature: %0.1f C" % data)
#            print("Humidity: %0.1f %%" % aht20.relative_humidity)
            print("sent")
            time.sleep(10)
            #  reset clock
            
        else:
            clock += 1
    # pylint: disable=broad-except
    #  any errors, reset Pico W
    except Exception as e:
#        print("Error:\n", str(e))
#        print("Resetting microcontroller in 10 seconds")
        time.sleep(10)
#        microcontroller.reset()
        data = microcontroller.cpu.temperature
        mqtt_client.publish(feed_names, data)
        print("Sent")
        time.sleep(5)
    #  delay
    time.sleep(1)
    print(clock)
