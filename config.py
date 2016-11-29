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

    def save_config(self):
        # Write Configuration
        j = ujson.dumps(self.config)
        with open('config.txt', 'wb') as f:
            f.write(j)

    def clean_config(self):
        self.config = {}
        self.save_config()

    def set_config(self, k, v):
        if v == '' or 'delete' in v :
            del self.config[k]
        else: self.config[k] = v

    def get_config(self, k=None):
        if k == None:
            return self.config
        if k in self.config:
            return self.config[k]
        else: return ''

config = Config()
