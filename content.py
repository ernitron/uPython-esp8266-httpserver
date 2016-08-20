# Content Callback functions.
# They should receive parameters and return a HTML formatted string
# By convention they start with cb_

import ujson
import gc
import time
from config import *
import ds18b20

# Global sensor
sensor = None

preamble1 = 'HTTP/1.1 %s\r\nServer: tempserver\r\nContent-Type: %s\r\n'
preamble2 = 'Cache-Control: private, no-store\r\nConnection: close\r\n\r\n'

#head = '<!DOCTYPE html>\n'\
#           '<html lang="en">\n<head>\n<title>Temp %s</title>\n%s' \
#           '<meta name="generator" content="esp8266-server">\n' \
#           '<meta charset="UTF-8">\n' \
#           '<meta name="viewport" content="width=device-width, initial-scale=1">\n' \
#           '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>\n' \
#           '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">\n' \
#           '<style media="screen" type="text/css">\n'\
#           'body {font-family: Georgia,serif;}\n</style>\n'\
#           '</head><body>\n'\
#           '<div class="container-fluid"><div class="jumbotron">\n'

# Must be called with parameters as in a = head % (title, refresh)
head1 = '<!DOCTYPE html>\n'\
        '<html lang="en">\n<head>\n<title>Temp %s</title>\n%s' \

head2 = '<meta charset="UTF-8">\n' \
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n' \
        '<script src="https://goo.gl/EWKTqQ"></script>\n' \
        '<link rel="stylesheet" href="http://goo.gl/E7UCvM">\n' \
        '<style media="screen" type="text/css">\n'\
        'body {font-family: Georgia,serif;}\n</style>\n'\
        '</head><body>\n'\
        '<div class="container-fluid"><div class="jumbotron">\n'

def cb_status():
    config = read_config()

    content  = '<h2>Status %s</h2>' \
               '<p>MacAddress %s' \
               '<p>Address %s' \
               '<p>Free Memory %d (alloc %d)</div>' % (config['chipid'], config['macaddr'], config['address'], gc.mem_free(), gc.mem_alloc())
    return content

def cb_setplace(place):
    config = read_config()

    config['place'] = place
    save_config(config)
    return 'Place set to %s' % place

def cb_setwifi(ssid, pwd):
    if len(ssid) < 3 or len(pwd) < 8:
        return '<h2>WiFi too short, try again</h2>'

    config = read_config()
    config['ssid'] = ssid
    config['pwd'] = pwd
    save_config(config)
    return '<h2>WiFi set to %s %s</h2>' % (ssid, pwd)

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
    if sensor == None:
        cb_temperature_init()

    try:
        temp, count, s = sensor.readtemp()
    except:
        sensor = None
        return '<h1><a href="/">No sensor</a></h1>' \

    place = 'Set Place'
    content = '<h1><a href="/">%s: %f °C</a></h1>' \
              '<p>Reading # %d @ %s' \
              '</p></div>' % (place, temp, count, s)
    return content

def cb_temperature_json(pin):
    global sensor
    temptable = {}
    if sensor == None:
        cb_temperature_init()

    try:
        temp, count, s = sensor.readtemp()
    except:
        sensor = None
    try:
        config = read_config()
    except:
        config['address'] = ''
        config['macaddr'] = ''
        config['place'] = 'Set place'

    temptable["temp"] = str(temp)
    temptable["count"] = str(count)
    temptable["mac"] = config['macaddr']
    temptable["server"] = config['address']
    temptable["date"] = time.time()
    temptable["place"] = config['place']
    temptable["sensor"] = s
    return ujson.dumps(temptable)

def httpheader(code, title, extension='h', refresh=''):
   codes = {'200':" OK", '400':" Bad Request", '404':" Not Found", '302':" Redirect"}
   try:
       httpstatus = str(code) + codes[str(code)]
   except:
       httpstatus = "501 Internal Server Error"

   # MIME types
   mt = {'h': "text/html", 'j': "application/json" }
   try:
       mimetype = mt[extension]
   except:
       mimetype = "text/plain"

   if extension == 'j':
       return [preamble1 % (httpstatus, mimetype), preamble2]
   else:
       return [preamble1 % (httpstatus, mimetype), preamble2, head1 % (title, refresh), head2]

footer_tail = '</div>' \
          '<footer class="footer"><div class="container">' \
          '<a href="/">[ index</a> | ' \
          '<a href="/temperature">temperature </a> | ' \
          '<a href="/j">json </a> | ' \
          '<a href="/setname">place</a> | ' \
          '<a href="/setwifi">wifi</a> | ' \
          '<a href="/status">status</a> | ' \
          '<a href="/reinit">reinit</a> | ' \
          '<a href="/help">help</a>]' \
          '</div></footer>' \
          '</body></html>'

def httpfooter():
    return footer_tail
