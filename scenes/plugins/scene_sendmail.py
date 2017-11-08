import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ..utils import screenshot


@pytest.mark.django_db
def shot_form(live_server, organizer, event, logged_in_client):
    event.plugins += ',pretix.plugins.sendmail'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/sendmail/'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/sendmail/form.png')
