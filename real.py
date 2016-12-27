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

def do_connect(ssid, pwd, TYPE, hard_reset=True):
    interface = network.WLAN(TYPE)

    # Stage zero if credential are null disconnect
    if not pwd or not ssid :
        print('Disconnecting ', TYPE)
        interface.active(False)
        return None

    if TYPE == network.AP_IF:
        interface.active(True)
        time.sleep_ms(200)
        interface.config(essid=ssid, password=pwd)
        return interface

    if hard_reset:
        interface.active(True)
        interface.connect(ssid, pwd)

    # Stage one check for default connection
    print('Connecting')
    for t in range(120):
        time.sleep_ms(250)
        if interface.isconnected():
            print('Yes! Connected')
            return interface
        if t == 60 and not hard_reset:
            # if still not connected
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
        print('wake from deep sleep')
        hard_reset = False
    else:
        hard_reset = True
        print('wake from hard reset')

    chipid = hexlify(machine.unique_id())

    # Read from file the whole configuration
    config.read_config()

    # Get WiFi defaults and connect
    ssid = config.get_config('ssid')
    pwd = config.get_config('pwd')
    interface = do_connect(ssid, pwd, network.STA_IF, hard_reset)

    # Turn on Access Point only with passw
    apssid = 'YoT-%s' % bytes.decode(chipid)
    appwd = config.get_config('appwd')
    if hard_reset:
        ap_interface = do_connect(apssid, appwd, network.AP_IF)

    if not interface and not ap_interface:
        print('Restart 10"')
        time.sleep(10.0)
        machine.reset()
        return

    # Set Parameters in configuration
    (address, mask, gateway, dns) = interface.ifconfig()
    config.set_config('address', address)
    config.set_config('mask', mask)
    config.set_config('gateway', gateway)
    config.set_config('dns', dns)
    config.set_config('mac', hexlify(interface.config('mac'), ':'))
    config.set_config('chipid', chipid)

    # Set Time RTC
    from ntptime import settime
    try:
        settime()
        (y, m, d, h, mm, s, c, u) = time.localtime()
        starttime = '%d-%d-%d %d:%d:%d UTC' % (y, m, d, h, mm, s)
    except:
        starttime = '2016-01-01 00:00:00'
        print('Cannot set time')

    # Set hostname
    interface.config(dhcp_hostname=chipid)
    config.set_config('hostname', interface.config('dhcp_hostname'))

    # We will save new configuration only at powerup
    if hard_reset:
        config.set_config('starttime', starttime)
        config.save_config()

    # Free some memory
    ssid = pwd = None
    apssid = appwd = None
    address = mask = gateway = dns = None
    gc.collect()

    # The application hook
    from application import application
    try:
        application(interface)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)

    # Restart
    print('Restarting')
    time.sleep(5.0)

    machine.reset()

