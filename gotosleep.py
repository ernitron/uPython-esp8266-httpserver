# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import machine

def gotosleep(sleep_timeout):
    # Remember for this to work GPIO16 (D0) must be connected to RST
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after a while (waking the device)
    sleep_timeout = sleep_timeout * 1000 # in microseconds
    rtc.alarm(rtc.ALARM0, sleep_timeout)

    # put the device to sleep
    print('Sleep for %d usec' % sleep_timeout)
    machine.deepsleep()
