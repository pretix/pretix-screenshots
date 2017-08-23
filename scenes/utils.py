import os

import time


def screenshot(client, name):
    time.sleep(1)
    os.makedirs(os.path.join('screens', os.path.dirname(name)), exist_ok=True)
    client.save_screenshot(os.path.join('screens', name))
