import os

import pytest
import time
from selenium.webdriver.common.by import By

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _

from ..utils import screenshot


@pytest.fixture
def items(event, tax_rule):
    i1 = event.items.create(name=_('Business Ticket'), default_price=400, admission=True, tax_rule=tax_rule,
                            active=True, position=2)
    i2 = event.items.create(name=_('Individual Ticket'), default_price=250, admission=True, tax_rule=tax_rule,
                            active=True, position=1)
    i3 = event.items.create(name=_('VIP Ticket'), default_price=600, admission=True, tax_rule=tax_rule,
                            active=True, position=3)
    c = event.categories.create(name=_('Merchandise'))
    i4 = event.items.create(name=_('T-Shirt'), default_price=25, admission=True, tax_rule=tax_rule,
                            active=True, category=c)
    v1 = i4.variations.create(value=_('S'))
    v2 = i4.variations.create(value=_('M'))
    v4 = i4.variations.create(value=_('L'), default_price=30)

    wc = event.categories.create(name=_('Workshops'))
    wc1 = event.items.create(name=_('Workshop session: Digital future'), default_price=12, active=True, category=wc)
    wc2 = event.items.create(name=_('Workshop session: Analog future'), default_price=12, active=True, category=wc)
    i1.addons.create(addon_category=wc, min_count=0, max_count=2)

    q1 = event.quotas.create(name=_('Available'), size=100)
    q1.items.add(i1)
    q1.items.add(i2)
    q1.items.add(i4)
    q1.items.add(wc1)
    q1.items.add(wc2)
    q1.variations.add(v1)
    q1.variations.add(v2)
    q1.variations.add(v4)
    q2 = event.quotas.create(name=_('Unavailable'), size=0)
    q2.items.add(i3)
    return [i1, i2, i3, i4, wc1, wc2]


SCREEN = None


@pytest.yield_fixture(params=["wide", "desktop", "mobile"])
def chrome_options(request, chrome_options):
    global SCREEN
    SCREEN = request.param

    chrome_options._arguments.remove('window-size=1366x768')
    chrome_options.add_argument('headless')
    if SCREEN == "wide":
        chrome_options.add_argument('window-size=1920x1080')
    elif SCREEN == "desktop":
        chrome_options.add_argument('window-size=1024x768')
    elif SCREEN == "mobile":
        chrome_options.add_experimental_option('mobileEmulation', {'deviceName': 'Pixel 2'})

    try:
        yield chrome_options
    finally:
        SCREEN = None
    return chrome_options


@pytest.yield_fixture(params=["stock", "custom_round"])
def color_opts(request, event):
    if request.param == "custom_round":
        event.settings.primary_color = '#ed0808'
        event.settings.theme_color_background = '#b20707'
    elif request.param == "custom_sharp":
        event.settings.primary_color = '#ed0808'
        event.settings.theme_color_background = '#000000'
        event.settings.theme_round_borders = False
    event.cache.clear()
    return request.param


@pytest.yield_fixture(params=["nolink", "link"])
def organizer_link_back(request, event):
    event.settings.organizer_link_back = (request.param == "link")
    return request.param


@pytest.yield_fixture(params=["en", "de,en"])
def lang_opts(request, event):
    event.settings.locales = request.param.split(',')
    event.settings.locale = request.param.split(',')[0]
    return request.param


@pytest.yield_fixture(params=["largeheader_title", "smallheader_title", "logo_title", "title"])
def pic_opts(request, event):
    if "largeheader" in request.param:
        value = open(os.path.join(os.path.dirname(__file__), "../../assets/eventheader_large.jpg"), "rb")
        newname = default_storage.save('logo.jpg', ContentFile(value.read()))
        event.settings.logo_image = 'file://' + newname
        event.settings.logo_image_large = True
    elif "smallheader" in request.param:
        value = open(os.path.join(os.path.dirname(__file__), "../../assets/eventheader_small.jpg"), "rb")
        newname = default_storage.save('logo.jpg', ContentFile(value.read()))
        event.settings.logo_image = 'file://' + newname
    elif "logo" in request.param:
        value = open(os.path.join(os.path.dirname(__file__), "../../assets/ticketshoplive_logo.png"), "rb")
        newname = default_storage.save('logo.jpg', ContentFile(value.read()))
        event.settings.logo_image = 'file://' + newname
    return request.param


@pytest.mark.django_db
def shot_shop_frontpage(live_server, organizer, event, items, color_opts, lang_opts, pic_opts,
                        client, organizer_link_back):
    event.live = True
    event.save()
    event.settings.waiting_list_enabled = True
    event.settings.waiting_list_auto = True

    client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    client.find_element(By.CSS_SELECTOR, "button[data-toggle=variations]")
    client.execute_script("window.scrollTo(0, 0)")
    time.sleep(1)
    screenshot(client, 'style/shop_frontpage_{}.png'.format('_'.join([
        SCREEN, color_opts, pic_opts, lang_opts, organizer_link_back
    ])))
