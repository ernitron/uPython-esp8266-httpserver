# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import time
import machine
import onewire
from ubinascii import hexlify

# The temp sensor DS18b20 with 4.7k Ohm resistor pull-up
# is on GPIO12 on Lolin V3 and WebMos D1-Mini
# Pin 12 is D6 on WeMos

class TempSensor():
  # D6	GPIO12	machine.Pin(12)
  def __init__(self, pin=12):
      self.read_count = 0
      self.sensor = 'none'
      # This is where the sensor is
      self.temp = '85.0' # the default error temperature of ds18b20
      dat = machine.Pin(pin)
      try:
          ow = onewire.OneWire(dat)
          self.ds = onewire.DS18B20(ow)
          self.present = True
      except:
          self.present = False
          self.ds = None

    #self.roms = self.ds.scan()
    #self.ds.convert_temp()
    #time.sleep_ms(750)
    #for rom in self.roms:
    #    self.temp = self.ds.read_temp(rom)
    #    self.read_count += 1
    #    self.present = True
    #    break # break at the first sensor

  def sensorid(self, rom):
      return hexlify(rom)

  def readtemp(self, n=1):
    if self.present == False:
        return ('85', 0, 'none')
    roms = self.ds.scan() # should we scan again?
    self.ds.convert_temp()
    time.sleep_ms(750)
    r = 1
    for rom in roms:
        self.temp = self.ds.read_temp(rom)
        self.sensor = self.sensorid(rom)
        if r >= n: break # break at the first sensor found
        self.present = True
        r += 1
    self.read_count += 1
    return (self.temp, self.read_count, self.sensor)

    def status(self):
        table = {}
        if self.present != False:
            table['temp'] = self.temp
            table['count'] = self.read_count
            table['sensor'] = self.sensor
            table['date'] = time.time()
        return table
