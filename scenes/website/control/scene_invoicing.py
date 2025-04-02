import random

import faker
import pytest
from selenium.webdriver.common.by import By
from django.utils.translation import gettext as _

from ...utils import screenshot


@pytest.mark.django_db
def shot_waiting_list_admin(live_server, organizer, event, logged_in_client):
    event.live = True
    event.settings.waiting_list_enabled = True
    event.settings.waiting_list_auto = True
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/invoice'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, "#id_invoice_address_required")
    screenshot(logged_in_client, 'website/control/invoice_settings.png')
