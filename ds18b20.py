# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import machine
import onewire

# The temp sensor DS18b20 with 4.7k Ohm resistor pull-up
# is on GPIO12 on Lolin V3 and WebMos D1-Mini
# Pin 12 is D6 on WeMos

class TempSensor():
  def __init__(self, pin=12):
    self.read_count = 0
    self.sensor_available = False
    self.sensor = 'null'
    self.temp = '85.0' # the default error temperature of ds18b20
    self.pin = pin # the default error temperature of ds18b20
    self.ds = None
    self.roms = []

  def scan(self):
    dat = machine.Pin(self.pin)
    ow = onewire.OneWire(dat)
    self.ds = onewire.DS18B20(ow)
    self.roms = self.ds.scan()
    self.ds.convert_temp()
    time.sleep_ms(750)
    self.temp = '85.0'
    for rom in self.roms:
        self.temp = self.ds.read_temp(rom)
        self.read_count += 1
        self.sensor_available = True
        break # break at the first sensor

  def sensorid(self, rom):
    sensor = '%x-' % rom[1]
    length = len(rom)-1
    for i in range(length):
        sensor += '%x' % rom[length-i-1]
    return sensor

  def readtemp(self, n=1):
    self.temp = '85.0'
    if self.sensor_available == False:
        return ([self.temp, 0, self.sensor])

    self.roms = self.ds.scan() # should we scan again?
    self.ds.convert_temp()
    time.sleep_ms(750)
    for rom in self.roms:
        self.temp = self.ds.read_temp(rom)
        self.sensor_available = True
        self.read_count += 1
        self.sensor = self.sensorid(rom)
        break

    return [self.temp, self.read_count, self.sensor]

