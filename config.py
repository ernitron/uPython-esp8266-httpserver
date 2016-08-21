import network
import ujson
import machine

config = {}
config_updated = False

def read_config():
    global config_updated
    global config
    # Get Configuration
    if config_updated == True:
        return config

    try:
        with open('config.txt', 'r') as f:
            c = f.read()
        config = ujson.loads(c)
        config_updated = True
    except:
        pass
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

def set_config(k,v):
    global config_updated
    global config
    config[k] = v
    config_updated = False

def update_config(sta_if):
    # Get Network Parameters
    (address, mask, gateway, dns) = sta_if.ifconfig()

    import ubinascii
    config['address'] = address
    config['mask'] = mask
    config['gateway'] = gateway
    config['dns'] = dns
    config['macaddr'] = ubinascii.hexlify(sta_if.config('mac'), ':')
    config['chipid'] = ubinascii.hexlify(machine.unique_id())
