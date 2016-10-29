# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Content Callback functions.
# They should receive parameters and return a HTML formatted string
# By convention they start with cb_

import gc
import time
import os
from config import save_config, set_config, get_config, clean_config

# Content Functions
def cb_index(title):
    with open('index.txt', 'r') as f:
        return f.readlines()
    return []

def cb_status():
    datetime = datenow()
    uptime = time.time()
    filesystem = os.listdir()
    chipid = get_config('chipid')
    macaddr = get_config('mac')
    address = get_config('address')
    starttime = get_config('starttime')
    return '<h2>Device %s</h2>' \
           '<p>MacAddr: %s' \
           '<p>Address: %s' \
           '<p>Free Mem: %d (alloc %d)' \
           '<p>Files: %s' \
           '<p>Uptime: %d' \
           '<p>Date Time: %s' \
           '<p>Start Time: %s'  \
           '</div>' % (chipid, macaddr, address, gc.mem_free(), gc.mem_alloc(), filesystem, uptime, datetime, starttime)

def cb_help():
    with open('help.txt', 'r') as f:
        return f.readlines()
    return []

def cb_resetconf():
    clean_config()
    return 'Config cleaned'

def cb_setparam(key, value):
    if value == None:
        if key != None: kvalue = 'value="%s"' % key
        else: kvalue = ' '
        with open('config.txt', 'r') as f:
            configuration = f.readlines()
        ret  = '<h2>Set configuration parameter</h2><form action="/conf">' \
               'Param <input type="text" %s name="key"> ' \
               'Value <input type="text" name="value"> ' \
               '<input type="submit" value="Submit">' \
               '</form></p>%s</div>' % (kvalue, configuration)
        return ret
    elif key in 'ssid' and len(value) < 3:
        return '<h2>WiFi too short, try again</h2>'
    elif key in 'pwd' and len(value) < 8:
        return '<h2>WiFi too short, try again</h2>'
    else:
        set_config(key, value)
        save_config()
    return '<h2>Param %s set to %s</h2>' % (key, value)

# Temperature sensor functions and global variable
sensor = None
def cb_temperature_init():
    import ds18b20
    global sensor
    if sensor != None:
        return True

    gc.collect()
    sensor = ds18b20.TempSensor()
    set_config('sensor', sensor.sensorid())
    try:
        save_config()
        return True
    except:
        print('TempSensor fail')
        sensor = None
        return False

def cb_temperature():
    global sensor
    if cb_temperature_init() == False:
        return '<h1><a href="/">No sensor</a></h1>'

    temp, count, s = sensor.readtemp()
    place = get_config('place')
    starttime = get_config('starttime')
    now = datenow()
    content = '<h1><a href="/">%s: %s °C</a></h1>' \
              '<p>Reading # %d @ %s' \
              '</p>Device started at %s</div>' % (place, str(temp), count, now, starttime)
    return content

def cb_temperature_json():
    global sensor
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
    temperaturedict["date"] = datenow()
    temperaturedict["sensor"] = s
    import json
    return json.dumps(temperaturedict)

def datenow():
    (Y, M, D, h, m, s, c, u) = time.localtime()
    h = (h+2) % 24 # TimeZone is GMT-2 hardcoded ;)
    return '%d-%d-%d %d:%d:%d' % (Y, M, D, h, m, s)

