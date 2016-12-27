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
def cb_open(filename):
    try:
        if filename == b'port_config.py': raise
        with open(filename, 'r') as f:
            return f.readlines()
    except:
        return ['No such file']

def cb_status():
    datetime = datenow()
    chipid = config.get_config('chipid')
    macaddr = config.get_config('mac')
    address = config.get_config('address')
    starttime = config.get_config('starttime')
    conf = json.dumps(config.get_config(None))
    return '<h2>Device %s</h2>' \
           '<p>MacAddr: %s' \
           '<p>Address: %s' \
           '<p>Free Mem: %d (alloc %d)' \
           '<p>Date Time: %s' \
           '<p>Start Time: %s'  \
           '</div>' % (chipid, macaddr, address, gc.mem_free(), gc.mem_alloc(), datetime, starttime)

def cb_getconf():
    return '<h2>Configuration</h2><p>%s</p>' % json.dumps(config.get_config(None))

def cb_setconf(key, value):
    if not value:
        if key:
            kvalue = 'value="%s"' % (key)
        else:
            kvalue = ''
        ret  = '<h2>Set configuration parameter</h2>'\
               '<form action="/setconf">' \
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

def cb_resetconf():
    config.clean_config()
    return 'Config cleaned'

def cb_listssid():
    response_header = '''
        <h1>Wi-Fi Client Setup</h1>
        <form action="/setconf" method="post">
          <label for="ssid">SSID</label>
          <select name="ssid" id="ssid">'''

    import network
    sta_if = network.WLAN(network.STA_IF)
    response_variable = ''
    for ssid, *_ in if_sta.scan():
        response_variable += '<option value="{0}">{0}</option>'.format(ssid.decode("utf-8"))

    response_footer = '''
           </select> <br/>
           Password: <input name="password" type="password"></input> <br />
           <input type="submit" value="Submit">
         </form>
    '''
    return response_header + response_variable + response_footer

# Temperature Sensor contents
from ds18b20 import sensor

def cb_temperature():
    T = sensor.status()
    place = config.get_config('place')
    starttime = config.get_config('starttime')
    content = '<h1><a href="/">%s: %s °C</a></h1>' \
              '<p>Sensor %s - Reading # %d @ %s' \
              '</p>Started on %s</div>' % (place, T['temp'], T['sensor'], T['count'], T['date'], starttime)
    return content

def cb_temperature_plain():
    T = sensor.status()
    content = '%s C' % T['temp']
    return content

def cb_temperature_json():
    T = sensor.status()
    return json.dumps(T)

def datenow():
    try:
        (Y, M, D, h, m, s, c, u) = time.localtime()
        return '%d-%d-%d %d:%d:%d' % (Y, M, D, h, m, s)
    except:
        return time.time()

