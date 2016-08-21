#!/usr/bin/python

import time
import network
import ds18b20
import gc
import config

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
        #print('STA config: ', sta_if.ifconfig())
    return sta_if

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE

if __name__ == '__main__':

    # Enable automatic garbage collector
    gc.enable()

    # Read configuration from file if exists
    config.read_config()
    print(config.config)

    if 'ssid' not in config.config:
        config.config['ssid'] = 'DefaultSSID'
        config.config['ssid'] = 'YpkeTron24'

    if 'pwd' not in config.config:
        config.config['pwd'] = 'DefaultPWD'
        config.config['pwd'] = 'BellaBrutta789'

    if 'place' not in config.config:
        config.config['place'] = 'Set Place'

    # Connect to Network and save if
    sta_if = do_connect(config.config['ssid'], config.config['pwd'])

    # Update config with new values
    config.update_config(sta_if)

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
    #    if development != True:
    #       machine.reset()


