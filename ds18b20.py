# Micropython
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import machine
import onewire

# The temp sensor DS18b20 with 4.7k Ohm resistor pull-up
# is on GPIO12 on Lolin V3 and WebMos D1-Mini

read_count = 0
ds = None
sensor_available = False

def init_temp_sensor(pin=12):
    global read_count
    global ds

    dat = machine.Pin(pin)
    ow = onewire.OneWire(dat)
    ds = onewire.DS18B20(ow)
    roms = ds.scan()
    ds.convert_temp()
    time.sleep_ms(750)
    try:
        rom = roms[n]
        temp = ds.read_temp(rom)
        read_count += 1
        sensor_available = True
    except:
        temp = '85.1' # Conventional Error for DS18b20
        sensor_available = False

def sensorid(rom):
    sensor = '%x-' % rom
    length = len(rom)-1
    for i in range(length):
        sensor += '%x' % rom[length-i-1]
    return sensor

def readtemp(n=1):

    global read_count
    global sensor_available
    if sensor_available == False:
        return ['85.0', read_count, 'No Sensor available']

    roms = ds.scan()
    ds.convert_temp()
    time.sleep_ms(750)
    try:
        rom = roms[n]
        temp = ds.read_temp(rom)
        read_count += 1
    except:
        t = '85.0' # Conventional Error for DS18b20
    sensor = sensorid(rom)

    return [temp, read_count, sensor]

