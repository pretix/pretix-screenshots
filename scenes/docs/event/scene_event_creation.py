import time

import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_event_creation(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/events/add')
    logged_in_client.find_element_by_css_selector("select[name='foundation-organizer'] option[value='%d']" % organizer.pk).click()
    logged_in_client.find_element_by_css_selector("input[name='foundation-locales'][value='en']").click()
    logged_in_client.find_element_by_css_selector("input[name='foundation-locales'][value='de']").click()
    screenshot(logged_in_client, 'event/create_step1.png')
    logged_in_client.find_element_by_css_selector(".submit-group .btn-primary").click()
    logged_in_client.find_element_by_css_selector("input[name='basics-name_0']").send_keys("Demo Conference")
    logged_in_client.find_element_by_css_selector("input[name='basics-slug']").send_keys("democon")
    logged_in_client.find_element_by_css_selector("input[name='basics-date_from_0']").send_keys("2018-02-01")
    logged_in_client.find_element_by_css_selector("input[name='basics-date_from_1']").send_keys("08:00:00")
    logged_in_client.find_element_by_css_selector("input[name='basics-date_to_0']").send_keys("2018-02-01")
    logged_in_client.find_element_by_css_selector("input[name='basics-date_to_1']").send_keys("18:00:00")
    logged_in_client.find_element_by_css_selector("input[name='basics-geo_lat']").click()
    screenshot(logged_in_client, 'event/create_step2.png')
    logged_in_client.find_element_by_css_selector(".submit-group .btn-primary").click()
    screenshot(logged_in_client, 'event/create_step3.png')
    logged_in_client.find_element_by_css_selector(".submit-group .btn-primary").click()
    screenshot(logged_in_client, 'event/create_step4.png')
