# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

import network
import ujson
import machine

config = {}
config_updated = False

def read_config():
    global config_updated
    global config
    # Get Configuration
    try:
        with open('config.txt', 'r') as f:
            c = f.read()
        config = ujson.loads(c)
    except:
        config = {}

    config_updated = True
    return config

def save_config():
    global config_updated
    global config
    # Write Configuration
    with open('config.txt', 'w') as f:
        j = ujson.dumps(config)
        f.write(j)
    config_updated = False
    return j

def clean_config():
    global config_updated
    import os
    os.remove('config.txt')
    config_updated = False

def set_config(k, v):
    global config_updated
    global config
    if v == '' or 'reset' in v :
        config[k] = None
    else: config[k] = v
    config_updated = False

def get_config(k):
    global config
    global config_updated
    if config_updated == False:
        read_config()
    if k in config:
        return config[k]
    else:
        return 'none'

