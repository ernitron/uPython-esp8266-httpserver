#!/usr/bin/python

import time    # Current time
import network
import machine
import gc
from config import *
import ds18b20

development = True

def do_connect(ssid, pwd):
    if ssid == None or pwd == None:
        return None

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        count = 0
        while not sta_if.isconnected():
            count += 1
            time.sleep_ms(200)
    return sta_if

def update_config(config, sta_if, ssid, pwd):

    # Get Network Parameters
    sta_if = network.WLAN(network.STA_IF)
    (address, mask, gateway, dns) = sta_if.ifconfig()

    import ubinascii
    config['address'] = address
    config['mask'] = mask
    config['gateway'] = gateway
    config['dns'] = dns
    config['macaddr'] = ubinascii.hexlify(sta_if.config('mac'), ':')
    config['chipid'] = ubinascii.hexlify(machine.unique_id())

    config['ssid'] = ssid
    config['pwd'] = pwd

    return config

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':
    # Enable automatic garbage collector
    gc.enable()

    # Load configuration from file if exists
    config = read_config()

    try:
        ssid = config['ssid']
        pwd = config['pwd']
    except:
        ssid = 'DefaultSSID'
        pwd = 'DefaultPWD'

    # Connect to Network and save if
    sta_if = do_connect(ssid, pwd)

    # Update config with new values
    update_config(config, sta_if, ssid, pwd)

    # Save configuration to file
    save_config(config)
    print ('Configuration ', config)

    # Do we have mem?
    mfree = gc.mem_free()
    if mfree < 10000:
        print('Memory Free : ', mfree)
        gc.collect()

    from httpserver import Server
    s = Server(8805)    # construct server object
    s.activate_server() # activate and run
    #try:
    #    s.activate_server() # activate and run
    #except KeyboardInterrupt:
    #    raise
    #except Exception:
#
#        if development != True:
#            machine.reset()


