import os

import time

from django.utils import translation


def screenshot(client, name):
    time.sleep(1)
    if translation.get_language() != 'en':
        p = name.rsplit('.', 1)
        p.insert(1, translation.get_language())
        name = '.'.join(p)
    os.makedirs(os.path.join('screens', os.path.dirname(name)), exist_ok=True)
    client.save_screenshot(os.path.join('screens', name))
