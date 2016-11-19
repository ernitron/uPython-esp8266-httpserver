# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Content Callback functions.
# They should receive parameters and return a HTML formatted string
# By convention they start with cb_

import gc
import time
import os
import json

# The configuration variable
from config import config

# Content Functions
def cb_index():
    with open('index.txt', 'r') as f:
        return f.readlines()
    return []

def cb_status():
    datetime = datenow()
    uptime = time.time()
    chipid = config.get_config('chipid')
    macaddr = config.get_config('mac')
    address = config.get_config('address')
    starttime = config.get_config('starttime')
    conf = json.dumps(config.get_config(None))
    return '<h2>Device %s</h2>' \
           '<p>MacAddr: %s' \
           '<p>Address: %s' \
           '<p>Free Mem: %d (alloc %d)' \
           '<p>Uptime: %d' \
           '<p>Date Time: %s' \
           '<p>Start Time: %s'  \
           '<p>Config: %s'  \
           '</div>' % (chipid, macaddr, address, gc.mem_free(), gc.mem_alloc(), uptime, datetime, starttime, conf)

def cb_help():
    with open('help.txt', 'r') as f:
        return f.readlines()
    return []

def cb_listssid():
    response_header = """
        <h1>Wi-Fi Client Setup</h1>
        <form action="configure" method="post">
          <label for="ssid">SSID</label>
          <select name="ssid" id="ssid">
    """

    response_variable = ""
    import network
    sta_if = network.WLAN(network.STA_IF)
    for ssid, *_ in if_sta.scan():
        response_variable += '<option value="{0}">{0}</option>'.format(ssid.decode("utf-8"))

    response_footer = """
           </select> <br/>
           Password: <input name="password" type="password"></input> <br />
           <input type="submit" value="Submit">
         </form>
    """
    return response_header + response_variable + response_footer

def cb_resetconf():
    config.clean_config()
    return 'Config cleaned'

def cb_setconf():
    config.save_config()
    return 'Config saved'

def cb_setparam(key, value):
    if value == None:
        if key != None: kvalue = 'value="%s"' % key
        else: kvalue = ' '
        ret  = '<h2>Set configuration parameter</h2><form action="/conf">' \
               'Param <input type="text" %s name="key"> ' \
               'Value <input type="text" name="value"> ' \
               '<input type="submit" value="Submit">' \
               '</form></p></div>' % (kvalue)
        return ret
    elif key in b'ssid' and len(value) < 3:
        return '<h2>WiFi too short, try again</h2>'
    elif key in b'pwd' and len(value) < 8:
        return '<h2>WiFi too short, try again</h2>'
    else:
        config.set_config(key, value)
        config.save_config()
    return '<h2>Param %s set to %s</h2>' % (key, value)


# Temperature Sensor contents
from ds18b20 import sensor
def cb_temperature_plain():
    return sensor.readtemp()

def cb_temperature():
    temp, count, s = sensor.readtemp()
    place = config.get_config('place')
    starttime = config.get_config('starttime')
    now = datenow()
    content = '<h1><a href="/">%s: %s °C</a></h1>' \
              '<p>Reading # %d @ %s' \
              '</p>Device started at %s</div>' % (place, str(temp), count, now, starttime)
    return content

def cb_temperature_json():
    temp, count, s = sensor.readtemp()
    config.set_config('sensor', sensor.sensorid())
    table = {}
    table["temp"] = str(temp)
    table["count"] = count
    table["mac"] = config.get_config('mac')
    table["server"] = config.get_config('address')
    table["place"] = config.get_config('place')
    table["chipid"] = config.get_config('chipid')
    table["date"] = datenow()
    table["sensor"] = s
    return json.dumps(table)

def datenow():
    (Y, M, D, h, m, s, c, u) = time.localtime()
    h = (h+2) % 24 # TimeZone is GMT-2 hardcoded ;)
    return '%d-%d-%d %d:%d:%d' % (Y, M, D, h, m, s)

