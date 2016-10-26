# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
from machine import Pin
import onewire, ds18x20
from ubinascii import hexlify

# The temp sensor DS18b20 with 4.7k Ohm resistor pull-up
# is on GPIO12 on Lolin V3 and WebMos D1-Mini
# Pin 12 is D6 on WeMos

class TempSensor():
  # D6	GPIO12	machine.Pin(12)
  def __init__(self, pin=12):
      self.read_count = 0
      self.sensor = 'none'
      self.temp = '85.0' # the default error temperature of ds18b20
      try:
          ow = onewire.OneWire(Pin(pin))
          self.ds = ds18x20.DS18X20(ow)
          self.present = True
      except:
          self.present = False
          self.ds = None

  def readtemp(self, n=1):
    if self.present == False:
        return ('85', self.read_count, 'none')
    roms = self.ds.scan() # should we scan again?
    self.ds.convert_temp()
    time.sleep_ms(750)
    self.temp = self.ds.read_temp(roms[n])
    self.sensor = hexlify(roms[n])
    self.read_count += 1
    self.present = True
    return (self.temp, self.read_count, self.sensor)

    def status(self):
        table = {}
        if self.present != False:
            table['temp'] = self.temp
            table['count'] = self.read_count
            table['sensor'] = self.sensor
            table['date'] = time.time()
        return table
