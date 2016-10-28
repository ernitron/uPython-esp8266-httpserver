# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import network
import machine
import gc

from ubinascii import hexlify
from config import read_config, get_config, set_config, save_config

def do_connect(ssid, pwd):
    sta_if = network.WLAN(network.STA_IF)
    if pwd == '' or ssid == '':
        #sta_if.active(False)
        print('NOT CONNECTED')
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

    # Start reading conf
    config = read_config()

    # Get defaults
    ssid = get_config('ssid')
    pwd = get_config('pwd')

    # Connect to Network and save if
    sta_if = do_connect(ssid, pwd)

    chipid = hexlify(machine.unique_id())
    set_config('chipid', chipid)

    # Turn on Access Point only if AP PWD is present
    apssid = 'YoT-%s' % bytes.decode(chipid)
    set_config('apssid', apssid)
    appwd = get_config('appwd')
    do_accesspoint(apssid, appwd)

    print('Sleep')
    time.sleep_ms(1000)

    # Update config with new values
    # Get Network Parameters
    if sta_if != None:
        (address, mask, gateway, dns) = sta_if.ifconfig()
        set_config('address', address)
        set_config('mask', mask)
        set_config('gateway', gateway)
        set_config('dns', dns)
        set_config('mac', hexlify(sta_if.config('mac'), ':'))

    # Set Time RTC
    from ntptime import settime
    settime()
    (y, m, d, h, mm, s, c, u) = time.localtime()
    set_config('starttime', '%d-%d-%d %d:%d:%d UTC' % (y, m, d, h, mm, s))

    # Ok now we save configuration!
    save_config()
    print(config)

    # Registering
    register_url = get_config('register')
    authorization = get_config('authorization')
    if register_url != '' and authorization != '':
        # When it starts send a register just to know we're alive
        from register import register
        tim = machine.Timer(-1)
        tim.init(period=300000, mode=machine.Timer.PERIODIC, callback=lambda t:register(register_url, authorization))


    # Free some memory
    ssid = pwd = None
    apssid = appwd = None
    config = None
    address = mask = gateway = dns = None
    gc.collect()

    # Launch Server
    from httpserver import Server
    s = Server(8805)    # construct server object
    try:
        s.activate_server() # activate and run
    except KeyboardInterrupt:
        raise
    except Exception:
        machine.reset()
