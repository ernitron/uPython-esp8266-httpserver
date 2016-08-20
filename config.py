import ujson

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

def save_config(conf):
    global config_updated
    # Write Configuration
    with open('config.txt', 'w') as f:
        f.write(ujson.dumps(conf))

    config_updated = False

