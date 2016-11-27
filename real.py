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

    # Stage zero if credential are null void connection
    if not pwd or not ssid :
        print('Disconnect from all known networks')
        sta_if.active(False)
        return None

    sta_if.active(True)

    # Stage one check for default connection
    print('Connecting')
    t = 0
    while t < 120:
        time.sleep_ms(500)
        if sta_if.isconnected():
            print('Yes! Connected')
            return sta_if
        if t == 60:  # if still not connected force
            print('Try ', ssid)
            sta_if.connect(ssid, pwd)
        t += 1

    # No way we are not connected
    print('Cant connect', ssid)
    return None

def do_accesspoint(ssid, pwd):
    ap_if = network.WLAN(network.AP_IF)
    if not pwd or not ssid :
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

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('woke from a deep sleep')
    else:
        print('power on or hard reset')

    # Read from file the whole configuration
    config.read_config()

    # Get chip id and previous one to compare them
    chipid = hexlify(machine.unique_id())
    chipid_config = config.get_config('chipid')

    # Get WiFi defaults and connect
    ssid = config.get_config('ssid')
    pwd = config.get_config('pwd')
    sta_if = do_connect(ssid, pwd)

    if sta_if == None:
        # Turn on Access Point only if AP PWD is present
        apssid = 'YoT-%s' % bytes.decode(chipid)
        appwd = config.get_config('appwd')
        sta_if = do_accesspoint(apssid, appwd)

    if sta_if != None:
        # Get Network Parameters
        (address, mask, gateway, dns) = sta_if.ifconfig()
        config.set_config('address', address)
        config.set_config('mask', mask)
        config.set_config('gateway', gateway)
        config.set_config('dns', dns)
        config.set_config('mac', hexlify(sta_if.config('mac'), ':'))
    else:
        print('Restart in 10')
        time.sleep(10.0)
        machine.reset()

    # We can set the time now
    config.set_time()

    # We will save new configuration only if we have changed chip
    if chipid != chipid_config:
        config.set_config('chipid', chipid)
        # Save configuration ONLY if it does not the same
        config.save_config()

    # Registering
    rurl = config.get_config('register')
    auth = config.get_config('authorization')
    if rurl and auth: # if both are not null
        from register import register
        # When it starts send a register just to know we're alive
        #tim = machine.Timer(-1)
        #tim.init(period=300000, mode=machine.Timer.PERIODIC, callback=lambda t:register(rurl, auth))

    # Free some memory
    ssid = pwd = None
    apssid = appwd = None
    address = mask = gateway = dns = None
    gc.collect()

    # Launch Server
    from httpserver import Server
    server = Server(8805)    # construct server object
    server.activate()        # server activate with
    try:
        server.wait_connections(sta_if) # activate and run for a while
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)

    # Restart
    print('Restart in 10')
    time.sleep(10.0)
    machine.reset()

    # If everything was ok we go to sleep for a while
    # from gotosleep import gotosleep
    #gotosleep()
