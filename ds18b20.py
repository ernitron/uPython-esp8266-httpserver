# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
from machine import Pin
from onewire import OneWire
import ds18x20
from ubinascii import hexlify

# The temp sensor DS18b20 with 4.7k Ohm resistor pull-up
# is on GPIO12 on Lolin V3 and WebMos D1-Mini
# Pin 12 is D6 on WeMos

class TempSensor():
  # D3	GPIO0	machine.Pin(0) no need external pullup resistor (preferred)
  # D4	GPIO2	machine.Pin(2) no need external pullup resistor
  # D6	GPIO12	machine.Pin(12) need 4.7kohm pullup resistor
  def __init__(self, pin=12):
      self.read_count = 0
      self.sensor = 'Null'
      self.temp = '85.0' # the default error temperature of ds18b20
      self.roms = None
      self.present = False
      try:
          ow = OneWire(Pin(pin))
          self.ds = ds18x20.DS18X20(ow)
          self.roms = self.ds.scan()
          self.present = True
      except:
          self.present = False
          self.ds = None

  def readtemp(self, n=0):
      if self.present == True:
         try:
           self.ds.convert_temp()
           time.sleep_ms(750)
           self.temp = self.ds.read_temp(self.roms[n])
           # 280b042800008019
           # 28-80000028040b
           self.sensor = hexlify(self.roms[n])
           self.read_count += 1
         except:
           self.temp = 85.0
           self.present = False
      return self.temp

  def sensorid(self):
      return self.sensor

  def status(self):
      self.readtemp()
      T = {}
      T['temp'] = str(self.temp)
      T['count'] = self.read_count
      T['sensor'] = self.sensor
      try:
          (Y, M, D, h, m, s, c, u) = time.localtime()
          h = (h+1) % 24 # TimeZone is GMT-2 hardcoded ;)
          T['date'] = '%d-%d-%d %d:%d:%d' % (Y, M, D, h, m, s)
      except:
          T['date'] = time.time()
      return T

sensor = TempSensor()
