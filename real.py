# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import sys
import network
import machine
import gc
from ubinascii import hexlify

from config import config

def do_connect(ssid, pwd, TYPE, force=False):
    interface = network.WLAN(TYPE)

    # Stage zero if credential are null void connection
    if not pwd or not ssid :
        print('Disconnect from all known networks')
        interface.active(False)
        return None

    if TYPE == network.AP_IF:
        interface.active(True)
        time.sleep_ms(200)
        interface.config(essid=ssid, password=pwd)
        return interface

    if force:
        interface.active(True)
        interface.connect(ssid, pwd)

    # Stage one check for default connection
    print('Connecting')
    for t in range(0, 120):
        time.sleep_ms(250)
        if interface.isconnected():
            #print('Yes! Connected')
            return interface
        if t == 60 and not force:
            # if still not connected force
            interface.active(True)
            interface.connect(ssid, pwd)

    # No way we are not connected
    print('Cant connect', ssid)
    return None

#----------------------------------------------------------------
# MAIN PROGRAM STARTS HERE
def main():

    # Enable automatic garbage collector
    gc.enable()

    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        print('woke from a deep sleep')
        force = False
    else:
        force = True
        print('power on or hard reset')

    # Read from file the whole configuration
    config.read_config()

    # Get chip id and previous one to compare them
    chipid = hexlify(machine.unique_id())
    chipid_config = config.get_config('chipid')

    # Get WiFi defaults and connect
    ssid = config.get_config('ssid')
    pwd = config.get_config('pwd')
    interface = do_connect(ssid, pwd, network.STA_IF, force)

    if not interface :
        # Turn on Access Point only if AP PWD is present
        apssid = 'YoT-%s' % bytes.decode(chipid)
        appwd = config.get_config('appwd')
        interface = do_connect(apssid, appwd, network.AP_IF)

    if interface :
        # Get Network Parameters
        (address, mask, gateway, dns) = interface.ifconfig()
        config.set_config('address', address)
        config.set_config('mask', mask)
        config.set_config('gateway', gateway)
        config.set_config('dns', dns)
        config.set_config('mac', hexlify(interface.config('mac'), ':'))
    else:
        print('Restart 10"')
        time.sleep(10.0)
        machine.reset()

    # We can set the time now
    # Set Time RTC
    from ntptime import settime
    try:
        settime()
        (y, m, d, h, mm, s, c, u) = time.localtime()
        starttime = '%d-%d-%d %d:%d:%d UTC' % (y, m, d, h, mm, s)
    except:
        starttime = ''
        print('Cannot set time')
        pass

    if force:
        config.set_config('starttime', starttime)

    # Set hostname
    interface.config(dhcp_hostname=chipid)
    config.set_config('hostname', interface.config('dhcp_hostname'))

    # Register at timeout // deprecated
    #rurl = config.get_config('register')
    #auth = config.get_config('authorization')
    #if rurl and auth: # if both are not null
        #from register import register
        # When it starts send a register just to know we're alive
        #tim = machine.Timer(-1)
        #tim.init(period=300000, mode=machine.Timer.PERIODIC, callback=lambda t:register(rurl, auth))

    # We will save new configuration only if we have changed chip
    if chipid != chipid_config:
        config.set_config('chipid', chipid)
        # Save configuration ONLY if it does not the same
        config.save_config()

    # Free some memory
    ssid = pwd = None
    apssid = appwd = None
    address = mask = gateway = dns = None
    gc.collect()

    # Launch Server
    from httpserver import Server
    server = Server()       # construct server object
    server.activate(8805)   # server activate with

    # now we introduce the sleep concept
    sleep = config.get_config('sleep')
    if not sleep: sleep = 300 # we stay awake for 30 secs and sleep for 300 (=5 minutes)

    try:
        server.wait_connections(interface, int(sleep/10)) # activate and run for a while
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.print_exception(e)
        print(e)

    # Restart
    print('Restarting')
    time.sleep(10.0)

    # If everything was ok we go to sleep for a while
    if sleep > 0:
        from gotosleep import gotosleep
        gotosleep(sleep)

    machine.reset()

