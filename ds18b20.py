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
  # D3	GPIO0	machine.Pin(0) no need external pullup resistor
  # D4	GPIO2	machine.Pin(2) no need external pullup resistor
  # D6	GPIO12	machine.Pin(12) need 4.7kohm pullup resistor
  def __init__(self, pin=12, place='', server='localhost', chipid='', mac=''):
      self.count = 0
      self.sensor = '000'
      self.temp = '85.0'    # the default error temperature of ds18b20
      self.place = place
      self.server = server
      self.chipid = chipid
      self.mac = mac
      try:
          ow = OneWire(Pin(pin))
          self.ds = ds18x20.DS18X20(ow)
          self.roms = self.ds.scan()
          self.present = True
      except:
          self.present = False

  def setplace(self, place='', server='localhost', chipid='', mac=''):
      if place: self.place = place
      if server: self.server = server
      if chipid: self.chipid = chipid
      if mac: self.mac = mac

  def temperature(self, n=0):
      if self.present :
         try:
           self.ds.convert_temp()
           time.sleep_ms(750)
           self.temp = self.ds.read_temp(self.roms[n])
           # 280b042800008019
           # 28-80000028040b
           self.sensor = hexlify(self.roms[n])
           self.count += 1
         except:
           self.temp = 85.0
           self.present = False
      return self.temp

  def sensorid(self):
      return self.sensor

  def status(self):
      self.temperature()
      T = {}
      T['temp'] = str(self.temp)
      T['count'] = self.count
      T['sensor'] = self.sensor
      T['server'] = self.server
      T['place'] = self.place
      T['chipid'] = self.chipid
      T['mac'] = self.mac
      try:
          (Y, M, D, h, m, s, c, u) = time.localtime()
          h = (h+1) % 24 # TimeZone is GMT-2 hardcoded ;)
          T['date'] = '%d-%d-%d %d:%d:%d' % (Y, M, D, h, m, s)
      except:
          T['date'] = ''
      return T

# The Sensor Class initialized to None
sensor = None
