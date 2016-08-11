#!/usr/bin/python

import socket  # Networking support
import time    # Current time
import network
import machine
import gc
import ujson

def do_connect(config):
    try:
        ssid = config['ssid']
        pwd  = config['pwd']
    except:
        ssid = 'YpkeTron24'
        pwd  = 'BellaBrutta789'

    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        count = 0
        while not sta_if.isconnected():
            count += 1
            time.sleep_ms(200)

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

def get_config():
    # Get Configuration
    config = {}
    try:
        with open('config.txt', 'r') as f:
            c = f.read()
        config = ujson.loads(c)
    except:
        pass
    return config

def set_config(config):
    # Write Configuration
    c = ujson.dumps(config)
    print('Configuration: ', c)
    with open('config.txt', 'w') as f:
        f.write(c)

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':
    # Enable automatic garbage collector
    gc.enable()

    # Load configuration from file if exists
    config = get_config()

    # Connect to Network
    config = do_connect(config)

    # Save configuration to file
    set_config(config)

    # Do we have mem?
    print ('Memory Free: ', gc.mem_free())

    from ds18b20 import *
    init_temp_sensor(12)

    from httpserver import Server
    s = Server(8805)    # construct server object
    s.activate_server() # activate and run

