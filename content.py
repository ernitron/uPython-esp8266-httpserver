# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Content Callback functions.
# They should receive parameters and return a HTML formatted string
# By convention they start with cb_

import gc
import time
from config import save_config, set_config, get_config
import ds18b20

# Content Functions
def cb_index(title):
    with open('index.txt', 'r') as f:
        return f.readlines()
    return []

def cb_status():
    uptime = time.time()
    import os
    filesystem = os.listdir()
    chipid = get_config('chipid')
    macaddr = get_config('mac')
    address = get_config('address')
    return '<h2>Device %s</h2>' \
           '<p>MacAddr: %s' \
           '<p>Address: %s' \
           '<p>Free Mem: %d (alloc %d)' \
           '<p>Files: %s' \
           '<p>Uptime: %d"</div>' % (chipid, macaddr, address, gc.mem_free(), gc.mem_alloc(), filesystem, uptime)

def cb_help():
    with open('help.txt', 'r') as f:
        return f.readlines()
    return []

def cb_setplace(place):
    set_config('place', place)
    save_config()
    return 'Place set to %s' % place

def cb_setparam(param, value):
    if param == None:
        return '<p>Set configuration parameter<form action="/conf">' \
               'Param <input type="text" name="param"> ' \
               'Value <input type="text" name="value"> ' \
               '<input type="submit" value="Submit">' \
               '</form></p></div>'
    else:
        set_config(param, value)
        save_config()
    return 'Param set to %s' % value

def cb_setwifi(ssid, pwd):
    if len(ssid) < 3 or len(pwd) < 8:
        return '<h2>WiFi too short, try again</h2>'
    set_config('ssid', ssid)
    set_config('pwd', pwd)
    save_config()
    return '<h2>WiFi set to %s %s</h2>' % (ssid, pwd)

# Temperature sensor functions and global variable
sensor = None
def cb_temperature_init():
    global sensor
    if sensor != None:
        return True
    gc.collect()
    try:
        sensor = ds18b20.TempSensor()
        return True
    except:
        print('TempSensor fail')
        sensor = None
        return False

def cb_temperature():
    if cb_temperature_init() == False:
        return '<h1><a href="/">No sensor</a></h1>' \

    temp, count, s = sensor.readtemp()
    place = get_config('place')
    uptime = time.time()
    content = '<h1><a href="/">%s: %s °C</a></h1>' \
              '<p>Reading # %d @ %d' \
              '</p></div>' % (place, str(temp), count, uptime)
    return content

def cb_temperature_json():
    if cb_temperature_init() == False:
        temp, count, s = (85.0, 0, '')
    else:
        temp, count, s = sensor.readtemp()

    temperaturedict = {}
    temperaturedict["temp"] = str(temp)
    temperaturedict["count"] = count
    temperaturedict["mac"] = get_config('mac')
    temperaturedict["server"] = get_config('address')
    temperaturedict["place"] = get_config('place')
    temperaturedict["chipid"] = get_config('chipid')
    temperaturedict["date"] = time.time()
    temperaturedict["sensor"] = s
    import json
    return json.dumps(temperaturedict)

