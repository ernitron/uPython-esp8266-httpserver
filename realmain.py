# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import network
import machine
import gc

from ubinascii import hexlify

from config import config

def do_connect(ssid, pwd):
    sta_if = network.WLAN(network.STA_IF)
    if pwd == '' or ssid == '':
        #sta_if.active(False)
        print('No connection')
        return None
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            time.sleep_ms(200)
        #print('STA config: ', sta_if.ifconfig())
    return sta_if

def do_accesspoint(ssid, pwd):
    ap_if = network.WLAN(network.AP_IF)
    if pwd == '' or ssid == '':
        ap_if.active(False)
        print('Disabling AP')
        return None
    ap_if.config(essid=ssid, password=pwd)
    ap_if.active(True)
    time.sleep_ms(200)
    print('AP config: ', ap_if.ifconfig())
    return ap_if

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE
def main():

    # Enable automatic garbage collector
    gc.enable()

    config.read_config()

    # Get defaults
    ssid = config.get_config('ssid')
    pwd = config.get_config('pwd')

    # Connect to Network and save if
    sta_if = do_connect(ssid, pwd)

    chipid = hexlify(machine.unique_id())
    config.set_config('chipid', chipid)

    # Turn on Access Point only if AP PWD is present
    apssid = 'YoT-%s' % bytes.decode(chipid)
    appwd = config.get_config('appwd')
    do_accesspoint(apssid, appwd)

    # To have time to press ^c
    time.sleep(2)

    # Update config with new values
    # Get Network Parameters
    if sta_if != None:
        (address, mask, gateway, dns) = sta_if.ifconfig()
        config.set_config('address', address)
        config.set_config('mask', mask)
        config.set_config('gateway', gateway)
        config.set_config('dns', dns)
        config.set_config('mac', hexlify(sta_if.config('mac'), ':'))

    # Ok now we save configuration!
    config.set_time()
    config.save_config()

    # Registering
    register_url = config.get_config('register')
    authorization = config.get_config('authorization')
    if register_url != '' and authorization != '':
        # When it starts send a register just to know we're alive
        from register import register
        tim = machine.Timer(-1)
        print('register init 5min')
        tim.init(period=300000, mode=machine.Timer.PERIODIC, callback=lambda t:register(register_url, authorization))

    # Free some memory
    ssid = pwd = None
    apssid = appwd = None
    address = mask = gateway = dns = None
    gc.collect()

    # Launch Server
    from httpserver import Server
    s = Server(8805)    # construct server object
    s.activate_server() # activate and run
    try:
        s.wait_connections() # activate and run
    except KeyboardInterrupt:
        raise
    except Exception:
        #machine.reset()
        pass
