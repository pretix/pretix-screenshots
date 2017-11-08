import pytest
import time

from decimal import Decimal
from django.conf import settings
from django_countries import Countries
from i18nfield.strings import LazyI18nString
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from ..utils import screenshot


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_tracking' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_tracking_settings(live_server, organizer, event, logged_in_client):
    event.plugins += ',pretix_tracking'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/tracking/settings'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/tracking/settings.png')
