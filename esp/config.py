""" Handles config file in persistent storage """
import os
import ujson as json

CONFIG_FILENAME = 'config.json'
CONFIG_DEFAULT = {
    'rate': 1,
    'delay_us': int(500e3)
}

_config = CONFIG_DEFAULT


def save():
    if CONFIG_FILENAME in os.listdir():
        os.remove(CONFIG_FILENAME)
    f = open(CONFIG_FILENAME, 'w')
    f.write(json.dumps(_config))
    f.close()


def get():
    return _config


def update(new_config):
    global _config
    _config = new_config
    save()


# Initialization
if CONFIG_FILENAME in os.listdir():
    f = open(CONFIG_FILENAME, 'r')
    _config = json.loads(f.read())
    print('Config loaded - ' + json.dumps(_config))

save()
