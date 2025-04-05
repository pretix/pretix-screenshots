import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ..utils import screenshot


@pytest.mark.django_db
@pytest.mark.xfail
def shot_pdf_editor(live_server, organizer, event, logged_in_client):
    event.plugins += ',pretix.plugins.ticketoutputpdf'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/pdfoutput/editor/'.format(
        organizer.slug, event.slug
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.ID, "editor-start"))
    )
    logged_in_client.find_element(By.ID, "editor-start").click()
    time.sleep(1.0)
    screenshot(logged_in_client, 'plugins/ticketoutputpdf/editor.png')
    logged_in_client.find_element(By.ID, "editor-preview").click()
