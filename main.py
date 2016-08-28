# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import network
import gc
import machine

from config import read_config, get_config, set_config, save_config

development = True

def do_connect(ssid, pwd):
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
    #print('AP config: ', ap_if.ifconfig())
    return ap_if

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':

    # Enable automatic garbage collector
    gc.enable()

    # Start reading conf
    config = read_config()

    # Some defaults
    if 'ssid' not in config: ssid = 'YpkeTron24'
    else: ssid = get_config('ssid')
    if 'pwd' not in config: pwd = 'BellaBrutta789'
    else: pwd = get_config('pwd')

    # Connect to Network and save if
    sta_if = do_connect(ssid, pwd)

    # Set here special parameters of this application so they can be modified
    if 'appwd' in config:
        pwd = get_config('appwd')
        chipid = get_config('chipid')
        ssid = 'YoT-'+chipid
        do_accesspoint(ssid, pwd)
    else:
        ap_if = network.WLAN(network.AP_IF)
        ap_if.active(False)

    # Update config with new values
    # Get Network Parameters
    (address, mask, gateway, dns) = sta_if.ifconfig()
    from ubinascii import hexlify
    set_config('address', address)
    set_config('mask', mask)
    set_config('gateway', gateway)
    set_config('dns', dns)
    set_config('mac', hexlify(sta_if.config('mac'), ':'))
    set_config('chipid', hexlify(machine.unique_id()))

    # Important config init values to be set
    if 'sensor' not in config :
        set_config('sensor', 'temp-generic')

    if 'develpment' not in config:
        development = True

    # Ok save it!
    save_config()

    # Free some memory
    ssid = pwd = None
    config = None

    # Registering
    register_url = get_config('register')
    authorization = get_config('authorization')
    if register_url != 'none' and authorization != 'none':
        from register import register
        tim = machine.Timer(-1)
        tim.init(period=5000, mode=machine.Timer.PERIODIC, callback=lambda t:register(register_url, authorization))

    gc.collect()

    # Launch Server
    from httpserver import Server
    s = Server(8805)    # construct server object
    try:
        s.activate_server() # activate and run
    except KeyboardInterrupt:
        raise
    except Exception:
        if development == False:
            machine.reset()

