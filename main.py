# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import ds18b20
import time
import network
import gc
from config import update_config, get_config


development = True

def do_connect(ssid, pwd):
    if ssid == None or pwd == None:
        return None

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            time.sleep_ms(200)
        print('STA config: ', sta_if.ifconfig())
    return sta_if

def do_accesspoint(ssid, pwd):
    ap_if = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=pwd)
    ap_if.active(True)
    time.sleep_ms(200)
    print('Access Point config: ', ap_if.ifconfig())
    return ap_if

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':

    # Enable automatic garbage collector
    gc.enable()

    ssid = get_config('ssid')
    pwd = get_config('pwd')
    place = get_config('place')

    # Connect to Network and save if
    sta_if = do_connect(ssid, pwd)

    # Update config with new values
    update_config(sta_if)

    # Access point is provided if in conf there are
    chipid = get_config('chipid')
    pwd = get_config('appwd')
    if pwd != 'none':
        ssid = 'YoT-'+chipid
        do_accesspoint(ssid, pwd)

    gc.collect()
    print(gc.mem_free())

    from httpserver import Server

    s = Server(8805)    # construct server object
    s.activate_server() # activate and run


