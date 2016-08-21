# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Content Callback functions.
# They should receive parameters and return a HTML formatted string
# By convention they start with cb_

import gc
import time
from config import config, read_config, save_config
import ujson
import ds18b20

# Global variables

head0 = 'HTTP/1.1 %s\r\nServer: tempserver\r\nContent-Type: %s\r\n'

head1 = 'Cache-Control: private, no-store\r\nConnection: close\r\n\r\n'

head2 = '<!DOCTYPE html>\n'\
        '<html lang="en">\n<head>\n<title>Temp %s</title>\n%s' \

head3 = '<meta charset="UTF-8">\n' \
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' \
        '<script src="https://goo.gl/EWKTqQ"></script>\n' \
        '<link rel="stylesheet" href="http://goo.gl/E7UCvM">\n' \
        '<style media="screen" type="text/css">\n'\
        'body {font-family: Georgia,serif;}\n</style>\n'\
        '</head><body>\n'\
        '<div class="container-fluid"><div class="jumbotron">\n'

foot1 = '</div><footer class="footer">'\
        '<a href="/">[ index</a> |'\
        '<a href="/temperature">temperature</a> |'\
        '<a href="/j">json</a> |'\
        '<a href="/setname">place</a> |'\
        '<a href="/setwifi">wifi</a> |'\
        '<a href="/status">status</a> |'\
        '<a href="/reinit">reinit</a> |'\
        '<a href="/help">help</a> ]'\
        '</footer>'

foot2 = '<p>Vers. 1.2.1</body></html>'

def httpheader(code, title, extension='h', refresh=''):
# HTML Codes
   codes = {200:" OK", 400:" Bad Request", 404:" Not Found", 302:" Redirect", 501: "Internal Server Error" }
# MIME types
   mt = {'h': "text/html", 'j': "application/json", 'p': "text/plain" }
   if code not in codes: code = 501
   httpstatus = str(code) + codes[code]

   if extension not in mt: extension = 'p'
   mimetype = mt[extension]

   if extension == 'j':
       return [head0 % (httpstatus, mimetype), head1]
   else:
       return [head0% (httpstatus, mimetype), head1, head2 % (title, refresh), head3]

def httpfooter():
    return [foot1, foot2]

# Content Functions

def cb_status():
    global config
    uptime = time.time()
    import os
    filesystem = os.listdir()
    return '<h2>Device %s</h2>' \
           '<p>MacAddr: %s' \
           '<p>Address: %s' \
           '<p>Free Mem: %d (alloc %d)' \
           '<p>Files: %s' \
           '<p>Uptime: %d"</div>' % (config['chipid'], config['macaddr'], config['address'], gc.mem_free(), gc.mem_alloc(), filesystem, uptime)

def cb_setplace(place):
    global config
    config['place'] = place
    save_config()
    return 'Place set to %s' % place

def cb_setwifi(ssid, pwd):
    global config
    if len(ssid) < 3 or len(pwd) < 8:
        return '<h2>WiFi too short, try again</h2>'
    config['ssid'] = ssid
    config['pwd'] = pwd
    save_config()
    return '<h2>WiFi set to %s %s</h2>' % (ssid, pwd)

# Temperature sensor functions and global variable
sensor = None

def cb_temperature_init():
    global sensor
    if sensor != None:
        # already initialized
        return sensor

    # finally import the sensor class
    try:
        sensor = ds18b20.TempSensor()
        sensor.scan()
    except:
        sensor = None
        return None
    return sensor

def cb_temperature():
    global sensor
    global config
    if sensor == None:
        cb_temperature_init()

    if 'place' in config:
        place = config['place']
    else:
        place = 'unknown'

    try:
        temp, count, s = sensor.readtemp()
    except:
        sensor = None
        return '<h1><a href="/">No sensor</a></h1>' \

    uptime = time.time()

    content = '<h1><a href="/">%s: %s °C</a></h1>' \
              '<p>Reading # %d @ %d' \
              '</p></div>' % (place, str(temp), count, uptime)
    return content

def cb_temperature_json(pin):
    global sensor
    global config
    if sensor == None:
        cb_temperature_init()
    try:
        temp, count, s = sensor.readtemp()
    except:
        sensor = None
        return "{'None'}"

    temperaturedict = {}
    temperaturedict["temp"] = str(temp)
    temperaturedict["count"] = str(count)
    if 'macaddr' in config:
        temperaturedict["mac"] = config['macaddr']
    if 'address' not in config:
        temperaturedict["server"] = config['address']
    temperaturedict["date"] = time.time()
    if 'place' in config:
        temperaturedict["place"] = config['place']
    temperaturedict["sensor"] = s
    return ujson.dumps(temperaturedict)

