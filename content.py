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

def cb_status():
    config = {}
    try:
        config = read_config()
    except:
        return '<h2>No Status</h2>'

    content  = '<h2>Status %s</h2>' % config['chipid']
    content += '<p>MacAddress %s' % config['macaddr']
    content += '<p>Address %s' % config['address']
    content += '<p>Free Memory %d (alloc %d)</div>' % (gc.mem_free(), gc.mem_alloc())
    return content

def cb_setplace(place):
    config = {}
    try:
        config = read_config()
    except:
        config = {}

    config['place'] = place
    save_config(config)
    return 'Place set to ' + place

def cb_setwifi(ssid, pwd):
    if len(ssid) < 3 or len(pwd) < 8:
        return '<h2>WiFi too short, try again</h2>'
    try:
        config = read_config()
    except:
        config = {}

    config['ssid'] = ssid
    config['pwd'] = pwd
    save_config(config)
    return '<h2>WiFi set to %s %s</h2>' % (ssid, pwd)

def cb_temperature_init():
    global sensor
    if sensor != None:
        # already initialized
        return sensor

    count = 10
    while count > 0:
        mfree = gc.mem_free()
        gc.collect()
        print(mfree)
        if mfree > 4800 :
            break
        else:
            count -= 1

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
    cb_temperature_init()
    content = '<h1><a href="/">No temp sensor available</a></h1>'
    if sensor == None:
        return content

    try:
        temp, count, sensor = sensor.readtemp()
    except:
        sensor = None
        return content

    place = 'Set Place'
    content = '<h1><a href="/">%s: %f C</a></h1>' \
              '<p>Reading # %d @ %s' \
              '</p></div>' % ( place, temp, count, sensor )
    return content

def cb_temperature_json(pin):
    global sensor
    cb_temperature_init()
    temptable = {}
    if sensor == None:
        return ujson.dumps(temptable)

    temp, count, s = sensor.readtemp()
    try:
        config = read_config()
    except:
        config['address'] = ''
        config['macaddr'] = ''

    temptable["temp"] = str(temp)
    temptable["mac"] = config['macaddr']
    temptable["server"] = config['address']
    temptable["count"] = str(count)
    temptable["date"] = time.time()
    temptable["sensor"] = s
    return ujson.dumps(temptable)

def httpheader(code, extension, title, refresh):
   codes = {'200':" OK", '400':" Bad Request", '404':" Not Found", '302':" Redirect"}
   try:
       HTTPStatusString = code + codes[code]
   except:
       HTTPStatusString = "501 Internal Server Error"

   # A few MIME types. Keep list short. If you need something that is missing, let's add it.
   mt = {'html': "text/html", 'json': "application/json" }
   try:
       MimeType = mt[extension]
   except:
       MimeType = "text/plain"

   if extension == 'json' :
       header = "HTTP/1.1 " + HTTPStatusString + "\r\nServer: tempserver\r\nContent-Type: " + MimeType + "\r\nCache-Control: private, no-store\r\n" + "Connection: close\r\n\r\n"
   else:
       header = "HTTP/1.1 " + HTTPStatusString + "\r\nServer: tempserver\r\nContent-Type: " + MimeType + "\r\nCache-Control: private, no-store\r\n" + "Connection: close\r\n\r\n" \
       '<!DOCTYPE html>\n' \
                 '<html lang="en">\n<head>\n<title>Temp ' + title + '</title>\n' + refresh + \
                 '<meta name="generator" content="esp8266-server">\n<meta charset="UTF-8">\n' \
                 '<meta name="viewport" content="width=device-width, initial-scale=1">\n' \
                 '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>\n' \
                 '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">\n' \
                 '<style media="screen" type="text/css">\n' \
                 'body {font-family: Georgia,serif;}\n.jumbotron {padding:10px 10px;}\n</style>\n' \
                 '</head>\n<body>\n' \
                 '<div class="container-fluid">\n<div class="jumbotron">\n'
   return header

def httpfooter():
   return '</div>' \
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
