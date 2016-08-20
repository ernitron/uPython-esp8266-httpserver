#!/usr/bin/python

import time    # Current time
import network
import machine
import gc
import config
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

def update_config(sta_if):
    # Get Network Parameters
    sta_if = network.WLAN(network.STA_IF)
    (address, mask, gateway, dns) = sta_if.ifconfig()

    import ubinascii
    config.config['address'] = address
    config.config['mask'] = mask
    config.config['gateway'] = gateway
    config.config['dns'] = dns
    config.config['macaddr'] = ubinascii.hexlify(sta_if.config('mac'), ':')
    config.config['chipid'] = ubinascii.hexlify(machine.unique_id())

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':

    # Enable automatic garbage collector
    gc.enable()

    # Load configuration from file if exists
    config.read_config()
    print (config.config)

    if 'ssid' not in config.config:
        config.config['ssid'] = 'DefaultSSID'

    if 'pwd' not in config.config:
        config.config['pwd'] = 'DefaultPWD'

    if 'place' not in config.config:
        config.config['place'] = 'Set Place'

    # Connect to Network and save if
    sta_if = do_connect(config.config['ssid'], config.config['pwd'])

    # Update config with new values
    update_config(sta_if)

    # Save configuration to file
    config.save_config()

    from httpserver import Server
    s = Server(8805, config.config['place'])    # construct server object
    s.activate_server() # activate and run
    #try:
    #    s.activate_server() # activate and run
    #except KeyboardInterrupt:
    #    raise
    #except Exception:
    #
    #    if development != True:
    #       machine.reset()


