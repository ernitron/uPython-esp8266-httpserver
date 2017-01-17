# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

#
from config import config
from display import display
import time

def application(interface) :

    mac = config.get_config('mac')
    server = config.get_config('address')
    place = config.get_config('place')
    chipid = config.get_config('chipid')

    # Temperature sensor device
    import ds18b20 as sensor
    # Now add some configuration params
    for pin in [12, 0, 2]:
        sensor.sensor = sensor.TempSensor(pin=pin, place=place, server=server, chipid=chipid, mac=mac)
        if sensor.sensor.present:
            print('Found sensor @', pin)
            break

    from register import Register
    rurl = config.get_config('register')
    auth = config.get_config('authorization')
    register = Register(rurl, auth)

    # http Server
    from httpserver import Server
    server = Server(title=place)       # construct server object
    server.activate(8805)   # server activate with port

    # now we introduce the sleep concept
    sleep = config.get_config('sleep')
    try:
        sleep = int(sleep)/10
    except:
        sleep = 0

    startime = time.time()
    while True:

        # activate and run for a while if returns True we go to sleep
        server.wait_connections(interface)

        T = sensor.sensor.status()
        display.display(T['temp'])

        delta = abs(time.time() - startime)
        if sleep and delta > sleep:
            register.http_post(T)
            from gotosleep import gotosleep
            gotosleep(int(sleep))
        elif delta > 300:
            register.http_post(T)
            startime = time.time()
