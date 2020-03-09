import time

import pytest
from django.conf import settings
from django.utils.translation import gettext as _, get_language

from ..plugins.scene_seating import seating_event, seating_plan, item_back, item_front, item_middle
from .frontend.scene_shop import items
from ..utils import screenshot

SCREEN = ""


@pytest.yield_fixture(params=["wide", "mobile"])
def chrome_options(request, chrome_options):
    global SCREEN
    SCREEN = request.param

    chrome_options._arguments.remove('window-size=1024x768')
    chrome_options.add_argument('headless')
    if SCREEN == "wide":
        chrome_options.add_argument('window-size=1200x675')
    elif SCREEN == "mobile":
        chrome_options.add_experimental_option('mobileEmulation', {'deviceName': 'Pixel 2'})

    try:
        yield chrome_options
    finally:
        SCREEN = None
    return chrome_options


@pytest.mark.usefixtures("seating_event")
@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_seating' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_with_seats(live_server, logged_in_client, organizer, event, seating_event):
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_elements_by_css_selector("svg circle.seat")[10].click()
    logged_in_client.find_elements_by_css_selector("svg circle.seat")[11].click()
    logged_in_client.find_elements_by_css_selector("svg circle.seat")[12].click()
    if SCREEN != "mobile":
        logged_in_client.find_elements_by_css_selector("select.frontrow-selected-item-variation-selection")[2].click()
    else:
        # Just de-focus
        logged_in_client.find_elements_by_css_selector(".fa-clock-o")[0].click()

    time.sleep(.5)
    screenshot(logged_in_client, 'website/landingpage/seating.{}.png'.format(SCREEN))


@pytest.mark.django_db
@pytest.mark.usefixtures("items")
@pytest.mark.skipif(
    'pretix_seating' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_without_seats(live_server, logged_in_client, organizer, event, items):
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    time.sleep(.5)
    screenshot(logged_in_client, 'website/landingpage/plain.{}.png'.format(SCREEN))
