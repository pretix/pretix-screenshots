import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ...utils import screenshot


@pytest.mark.django_db
def shot_waiting_list_admin(live_server, organizer, event, logged_in_client):
    event.live = True
    event.settings.waiting_list_enabled = True
    event.settings.waiting_list_auto = True
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/pdfoutput/editor/'.format(
        organizer.slug, event.slug
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#editor-start"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'website/control/pdfticket_editor.png')
