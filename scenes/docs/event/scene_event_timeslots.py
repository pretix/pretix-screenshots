import datetime
import time

import pytest
from django.utils.formats import date_format
from django.utils.timezone import now
from django.utils.translation import gettext as _
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from ...utils import screenshot


@pytest.mark.django_db
def shot_create(live_server, organizer, event, logged_in_client):
    event.has_subevents = True
    event.live = True
    event.testmode = False
    event.name = _("Museum")
    event.save()
    event.settings.event_list_type = 'week'

    i1 = event.items.create(name=_('Entry for adults'), default_price=23)
    i2 = event.items.create(name=_('Entry for children'), default_price=19)

    logged_in_client.get(live_server.url + '/control/event/{}/{}/subevents/bulk_add'.format(
        organizer.slug, event.slug,
    ))
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-weekly_byweekday'][value='TU']").click()
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-weekly_byweekday'][value='WE']").click()
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-weekly_byweekday'][value='TH']").click()
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-weekly_byweekday'][value='FR']").click()
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-weekly_byweekday'][value='SA']").click()
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-until']").clear()
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-until']").send_keys(
        date_format(now() + datetime.timedelta(days=30), 'SHORT_DATETIME_FORMAT')
    )
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-end'][value='until']").click()
    logged_in_client.find_element_by_css_selector("#time-formset [data-formset-add]").click()
    logged_in_client.find_element_by_css_selector("#time-formset [data-formset-add]").click()
    logged_in_client.find_element_by_css_selector("input[name='timeformset-0-time_from']").send_keys('10:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-0-time_to']").send_keys('11:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-1-time_from']").send_keys('11:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-1-time_to']").send_keys('12:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-2-time_from']").send_keys('12:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-2-time_to']").send_keys('13:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-3-time_from']").send_keys('13:00:00')
    logged_in_client.find_element_by_css_selector("input[name='timeformset-3-time_to']").send_keys('14:00:00')
    logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-interval']").click()
    logged_in_client.execute_script("window.scrollTo(0, 0)")
    screenshot(logged_in_client, 'event/timeslots_create.png')
    logged_in_client.execute_script(
        "arguments[0].scrollIntoView();",
        logged_in_client.find_element_by_css_selector("input[name='rruleformset-0-until']")
    )
    logged_in_client.find_element_by_css_selector("input[name='name_0']").send_keys(event.name)
    screenshot(logged_in_client, 'event/timeslots_create_2.png')
    logged_in_client.execute_script(
        "arguments[0].scrollIntoView();",
        logged_in_client.find_element_by_css_selector("input[name='quotas-0-name']")
    )
    logged_in_client.find_element_by_css_selector("input[name='quotas-0-name']").send_keys(event.name)
    logged_in_client.find_element_by_css_selector("input[name='quotas-0-size']").send_keys('50')
    logged_in_client.find_element_by_css_selector(
        "input[name='quotas-0-itemvars'][value='{}']".format(i1.pk)
    ).click()
    logged_in_client.find_element_by_css_selector(
        "input[name='quotas-0-itemvars'][value='{}']".format(i2.pk)
    ).click()
    screenshot(logged_in_client, 'event/timeslots_create_3.png')
    logged_in_client.find_element_by_css_selector(".btn-save").click()
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
    )

    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/#tab-0-6-open'.format(
        organizer.slug, event.slug,
    ))
    logged_in_client.execute_script(
        "arguments[0].scrollIntoView();",
        logged_in_client.find_elements_by_css_selector(".btn-save")[-1]
    )
    logged_in_client.find_element_by_css_selector("select[name='settings-event_list_type']").click()
    screenshot(logged_in_client, 'event/timeslots_settings_1.png')

    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug,
    ))
    screenshot(logged_in_client, 'event/timeslots_presale.png')

    logged_in_client.get(live_server.url + '/control/event/{}/{}/checkinlists/add#tab-0-1-open'.format(
        organizer.slug, event.slug,
    ))
    logged_in_client.execute_script(
        "arguments[0].scrollIntoView();",
        logged_in_client.find_element_by_css_selector(".checkin-rule-addchild")
    )
    logged_in_client.find_elements_by_css_selector(".checkin-rule-addchild")[0].click()
    logged_in_client.find_elements_by_css_selector(".checkin-rule-addchild")[0].click()
    logged_in_client.find_elements_by_css_selector(".checkin-rule-addchild")[0].click()

    s = logged_in_client.find_elements_by_css_selector(".checkin-rule select")[1]
    Select(s).select_by_value('now')
    logged_in_client.execute_script(
        'arguments[0].dispatchEvent(new Event("input")); ',
        s
    )
    time.sleep(.5)

    s = logged_in_client.find_elements_by_css_selector(".checkin-rule select")[2]
    Select(s).select_by_value('isAfter')
    logged_in_client.execute_script(
        'arguments[0].dispatchEvent(new Event("input")); ',
        s
    )
    time.sleep(.5)

    s = logged_in_client.find_elements_by_css_selector(".checkin-rule select")[3]
    Select(s).select_by_value('date_from')
    logged_in_client.execute_script(
        'arguments[0].dispatchEvent(new Event("input")); ',
        s
    )

    s = logged_in_client.find_elements_by_css_selector(".checkin-rule select")[4]
    Select(s).select_by_value('now')
    logged_in_client.execute_script(
        'arguments[0].dispatchEvent(new Event("input")); ',
        s
    )
    time.sleep(.5)

    s = logged_in_client.find_elements_by_css_selector(".checkin-rule select")[5]
    Select(s).select_by_value('isBefore')
    logged_in_client.execute_script(
        'arguments[0].dispatchEvent(new Event("input")); ',
        s
    )
    time.sleep(.5)

    s = logged_in_client.find_elements_by_css_selector(".checkin-rule select")[6]
    Select(s).select_by_value('date_to')
    logged_in_client.execute_script(
        'arguments[0].dispatchEvent(new Event("input")); ',
        s
    )
    time.sleep(.5)
    logged_in_client.execute_script(
        "arguments[0].scrollIntoView();",
        logged_in_client.find_elements_by_css_selector(".btn-save")[-1]
    )
    screenshot(logged_in_client, 'event/timeslots_checkinlists.png')
