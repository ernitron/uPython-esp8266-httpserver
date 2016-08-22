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
        config_updated = True
    except:
        pass

    print(config)
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

def set_config(k, v):
    global config_updated
    global config
    config[k] = v
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

def update_config(sta_if):
    global config_updated
    global config

    # Get Network Parameters
    (address, mask, gateway, dns) = sta_if.ifconfig()

    import ubinascii
    config['address'] = address
    config['mask'] = mask
    config['gateway'] = gateway
    config['dns'] = dns
    config['macaddr'] = ubinascii.hexlify(sta_if.config('mac'), ':')
    config['chipid'] = ubinascii.hexlify(machine.unique_id())

    save_config()

