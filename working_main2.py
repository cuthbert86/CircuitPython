# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT
#import circuitpython_csv as csv
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
from collections import deque
import time
import re
import storage
import adafruit_dht
import adafruit_datetime

dhtDevice = adafruit_dht.DHT22(board.GP19)
temperature_c = dhtDevice.temperature
temperature_f = temperature_c * (9 / 5) + 32
humidity = dhtDevice.humidity
print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
)




def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

    unix_time = 1660764970 # Wed Aug 17 2022 19:36:10 GMT+0000
    tz_offset_seconds = -14400  # NY Timezone

    get_timestamp = int(unix_time + tz_offset_seconds)
    current_unix_time = time.localtime(get_timestamp)
    current_struct_time = time.struct_time(current_unix_time)
    current_date = "{}".format(_format_datetime(current_struct_time))

    print("Timestamp:", current_date)

Data_point_size = 100
dq = deque([], Data_point_size)


#all_files = os.listdir()  ## List all files in directory
#if "datalog.csv" not in all_files:
#    with open("datalog.csv", mode="w", encoding="utf-8") as writablefile:
#        csvwriter = csv.writer(writablefile)
#        csvwriter.writerow([data, _format_datetime])


#def data_csv(data, timestamp):
#    with open("datalog.csv", mode="a", encoding="utf-8") as writablefile:
#        csvwriter = csv.writer(writablefile)
#        csvwriter.writerow([data, _format_datetime])
#        dq.append(data)

aio_username = "CuthbertB"
aio_key = "secret key"



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

#aio_username = "CuthbertB"
#aio_key = os.getenv("aio_zeeY22wcQSYizgJ1Y0fjsLM1NtZy")

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)
print("connected to io")

#  use Pico W's GP0 for SDA and GP1 for SCL
#i2c = busio.I2C(board.GP1, board.GP0)
#aht20 = adafruit_ahtx0.AHTx0(i2c)

try:
# get feed
    picowTemp_feed = aio_username + "/feeds/temperature_c"
#    picowTemp_feed = io.get_feed("temperature")
    print("connected to temperature_c")
    picowHumid_feed =  aio_username + "/feeds/pihumid"
except AdafruitIO_RequestError:
# if no feed exists, create one
    picowTemp_feed = io.create_new_feed("temperature_c")
    picowHumid_feed = io.create_new_feed("pihumid")

#  pack feed names into an array for the loop
feed_names = picowTemp_feed
feed_humid = picowHumid_feed
print("feeds created")

clock = 300

while True:
    try:
        #  when the clock runs out..
        if clock > 300:
            #  read sensor
            dhtDevice = adafruit_dht.DHT22(board.GP19)
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
            )
            
            mqtt_client.publish(feed_names, temperature_c)
            mqtt_client.publish(feed_humid, humidity)
            print("Sent")
            time.sleep(10)
            #  print sensor data to the REPLtime.sleep(10)
            #  reset clock
                        #  read sensor
            dhtDevice = adafruit_dht.DHT22(board.GP19)
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
            )
            
            mqtt_client.publish(feed_names, temperature_c)
            mqtt_client.publish(feed_humid, humidity)
            print("Sent")
            time.sleep(10)
        else:
            clock += 1
    # pylint: disable=broad-except
    #  any errors, reset Pico W
    except Exception as e:
            #  read sensor
 #           dhtDevice = adafruit_dht.DHT22(board.GP19)
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(temperature_f, temperature_c, humidity)
            )
            
            mqtt_client.publish(feed_names, temperature_c)
            mqtt_client.publish(feed_humid, humidity)
            print("Sent")
            time.sleep(10)
    #  delay
    time.sleep(1)
    print(clock)
