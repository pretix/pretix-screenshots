import os
import random
import datetime
import time

import pytest
import pytz
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.timezone import now
from django.utils.translation import gettext as _
from pretix.presale.style import regenerate_css

# fixtures from elsewhere
from ..plugins.scene_seating import seating_event, seating_plan, item_back, item_front, item_middle
from .frontend.scene_shop import items

from ..utils import screenshot

SCREEN = ""


@pytest.fixture
def swimming_series(event):
    event.has_subevents = True
    event.name = _('Swimming pool')
    event.date_to = None
    event.date_from = event.date_from.replace(hour=19)
    event.location = _('River street 6\nHeidelberg')
    event.save()
    event.settings.event_list_type = 'weeks'
    event.settings.primary_font = 'Lato'

    d = now() + datetime.timedelta(days=(8 - now().isoweekday()))
    quotas = [5, 0, 5, 5, 5, 0, 5, 5, 0, 5, 5, 5, 5]
    while d < now() + datetime.timedelta(days=60):
        for start, end in [(datetime.time(7, 0, 0), datetime.time(9, 0, 0)), (datetime.time(9, 0, 0), datetime.time(18, 0, 0)),
                           (datetime.time(18, 0, 0), datetime.time(22, 0, 0))]:
            se = event.subevents.create(
                active=True,
                is_public=True,
                name="Slot",
                date_from=datetime.datetime.combine(d.date(), start, tzinfo=pytz.UTC),
                date_to=datetime.datetime.combine(d.date(), end, tzinfo=pytz.UTC),
            )
            size = quotas.pop(0)
            quotas.append(size)
            q = se.quotas.create(event=event, name="Q", size=size)
            q.items.set(event.items.all())

        d += datetime.timedelta(days=1)

    value = open(os.path.join(os.path.dirname(__file__), "../../assets/swimming_header.png"), "rb")
    newname = default_storage.save('logo.jpg', ContentFile(value.read()))
    event.settings.logo_image = 'file://' + newname
    event.settings.logo_image_large = True
    event.settings.primary_color = '#244bb3'
    event.settings.theme_color_background = '#e6e6ff'
    event.settings.event_list_type = 'week'

    regenerate_css.apply_async(args=(event.pk,))
    return event


@pytest.fixture
def workshop_series(event):
    event.has_subevents = True
    event.name = _('')
    event.date_to = None
    event.date_from = event.date_from.replace(hour=19)
    event.location = _('Learning Hub\nEmmy-Noether-Street 5\nHeidelberg')
    event.save()

    texts = [
        _('HTML for beginners'),
        _('CSS for beginners'),
        _('JavaScript for beginners'),
        _('Advanced HTML course'),
        _('CSS deep-dive workshop'),
        _('HTML for beginners'),
        _('CSS for beginners'),
        _('JavaScript for beginners'),
        _('Advanced HTML course'),
        _('CSS deep-dive workshop'),
    ]
    for i, t in enumerate(texts):
        event.subevents.create(
            active=True,
            is_public=True,
            name=t,
            date_from=datetime.datetime.combine(now().date() + datetime.timedelta(days=5 + 2 ** i), datetime.time(9, 0, 0), tzinfo=pytz.UTC),
        )
    for i, se in enumerate(event.subevents.all()):
        q = se.quotas.create(event=event, name="Q", size=0 if i == 2 else 10)
        q.items.set(event.items.all())

    value = open(os.path.join(os.path.dirname(__file__), "../../assets/workshop_header.jpg"), "rb")
    newname = default_storage.save('logo.jpg', ContentFile(value.read()))
    event.settings.logo_image = 'file://' + newname
    event.settings.logo_image_large = True
    event.settings.primary_color = '#0282BE'
    event.settings.theme_color_background = '#91C6E7'
    event.settings.event_list_type = 'list'
    event.settings.primary_font = 'Fira Sans'
    event.settings.logo_show_title = True
    event.settings.waiting_list_enabled = True

    regenerate_css.apply_async(args=(event.pk,))
    return event


@pytest.yield_fixture(params=["wide", "mobile"])
def chrome_options(request, chrome_options):
    global SCREEN
    SCREEN = request.param

    chrome_options._arguments = [a for a in chrome_options._arguments if 'window-size' in a]
    chrome_options.add_argument('headless')
    chrome_options.add_argument('hide-scrollbars')
    if SCREEN == "wide":
        chrome_options.add_argument('window-size=1536x864')
    elif SCREEN == "mobile":
        chrome_options.add_argument('window-size=432x936')
        # chrome_options.add_experimental_option('mobileEmulation', {'deviceName': 'Pixel 5'})

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
    event.settings.theme_color_background = '#f5f5f5'
    regenerate_css.apply_async(args=(event.pk,))
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    time.sleep(.5)
    screenshot(logged_in_client, 'website/landingpage/conference.{}.png'.format(SCREEN))


@pytest.mark.django_db
@pytest.mark.usefixtures("items")
def shot_swimming(live_server, swimming_series, logged_in_client, organizer, event, items):
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    time.sleep(.5)
    logged_in_client.execute_script('$("details").prop("open", true)')
    screenshot(logged_in_client, 'website/landingpage/swimming.{}.png'.format(SCREEN))


@pytest.mark.django_db
@pytest.mark.usefixtures("items")
def shot_workshops(live_server, workshop_series, logged_in_client, organizer, event, items):
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    time.sleep(.5)
    logged_in_client.execute_script('$("details").prop("open", true)')
    screenshot(logged_in_client, 'website/landingpage/workshops.{}.png'.format(SCREEN))


@pytest.fixture
def items_museum(event, tax_rule):
    i1 = event.items.create(name=_('Full-price entry'), default_price=12.50, admission=True, tax_rule=tax_rule,
                            active=True, position=1)
    i2 = event.items.create(name=_('Reduced ticket'), description=_('For students and children younger than 14 years.'), default_price=9.50,
                            admission=True, tax_rule=tax_rule,
                            active=True, position=2)
    i3 = event.items.create(name=_('Children ticket'), description=_('Only for children younger than 6 years.'), default_price=0,
                            admission=True, tax_rule=tax_rule,
                            active=True, position=3)
    c = event.categories.create(name=_('Add-ons'))
    wc1 = event.items.create(name=_('Audio Guide'), default_price=5, active=True, category=c, tax_rule=tax_rule)

    q1 = event.quotas.create(name=_('Available'), size=100)
    q1.items.add(i1)
    q1.items.add(i2)
    q1.items.add(i3)
    q1.items.add(wc1)


@pytest.mark.django_db
@pytest.mark.usefixtures("items_museum")
def shot_museum(live_server, logged_in_client, organizer, event, items_museum):
    value = open(os.path.join(os.path.dirname(__file__), "../../assets/museum_header.png"), "rb")
    newname = default_storage.save('logo.jpg', ContentFile(value.read()))
    event.settings.logo_image = 'file://' + newname
    event.settings.logo_image_large = True
    event.settings.theme_color_background = '#E6E6FF'
    event.settings.primary_color = '#46447c'
    event.settings.primary_font = 'Titillium'
    event.settings.show_dates_on_frontpage = False
    event.name = 'Art Museum'
    event.location = _('Caspar-David-Friedrich Street 42\nHeidelberg')
    event.save()
    regenerate_css.apply_async(args=(event.pk,))
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    time.sleep(.5)
    screenshot(logged_in_client, 'website/landingpage/museum.{}.png'.format(SCREEN))
