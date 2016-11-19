# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import network
import ujson
import machine
import time

class Config():
    def __init__(self):
        self.config = {}

    def read_config(self):
        try:
            with open('config.txt', 'rb') as f:
                c = f.read()
            self.config = ujson.loads(c)
        except:
            self.config = {}

    def set_time(self):
        # Set Time RTC
        from ntptime import settime
        try:
            settime()
            (y, m, d, h, mm, s, c, u) = time.localtime()
            self.config['starttime'] = '%d-%d-%d %d:%d:%d UTC' % (y, m, d, h, mm, s)
        except:
            print('Cannot set time')
            pass

    def save_config(self):
        # Write Configuration
        with open('config.txt', 'wb') as f:
            j = ujson.dumps(self.config)
            f.write(j)
        return j

    def clean_config(self):
        self.config = {}
        self.save_config()

    def set_config(self, k, v):
        if v == '' or 'reset' in v :
            self.config[k] = None
        else: self.config[k] = v

    def get_config(self, k=None):
        if k == None:
            return self.config
        if k in self.config:
            return self.config[k]
        else: return ''

config = Config()
