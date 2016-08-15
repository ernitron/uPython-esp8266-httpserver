import ujson

def get_config():
    # Get Configuration
    config = {}
    try:
        with open('config.txt', 'r') as f:
            c = f.read()
        config = ujson.loads(c)
    except:
        pass
    return config

def set_config(config):
    # Write Configuration
    c = ujson.dumps(config)
    print('Configuration: ', c)
    with open('config.txt', 'w') as f:
        f.write(c)
