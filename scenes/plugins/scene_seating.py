import os
import time

import pytest
import random
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _, get_language

from pretix.base.models import SeatingPlan, Event
from pretix.base.services.seating import generate_seats
from pretix.presale.style import regenerate_css
from ..utils import screenshot


@pytest.fixture
def seating_plan(organizer, tax_rule):
    with open(os.path.join(os.path.dirname(__file__), 'plan.{}.json'.format(get_language()))) as r:
        return SeatingPlan.objects.create(
            organizer=organizer,
            name=_("Main hall"),
            layout=r.read()
        )


@pytest.fixture
def item_front(event, tax_rule):
    i = event.items.create(
        name=_('Category 1'), default_price=23, admission=True,
        tax_rule=tax_rule
    )
    i.variations.create(value=_('Regular'))
    i.variations.create(value=_('Student'), default_price=19)
    return i


@pytest.fixture
def item_middle(event, tax_rule):
    i = event.items.create(
        name=_('Category 2'), default_price=19, admission=True,
        tax_rule=tax_rule
    )
    i.variations.create(value=_('Regular'))
    i.variations.create(value=_('Student'), default_price=15)
    return i


@pytest.fixture
def item_back(event, tax_rule):
    i = event.items.create(
        name=_('Category 3'), default_price=15, admission=True,
        tax_rule=tax_rule
    )
    i.variations.create(value=_('Regular'))
    i.variations.create(value=_('Student'), default_price=13)
    return i


@pytest.fixture
def seating_event(event: Event, seating_plan, item_front, item_middle, item_back):
    event.seat_category_mappings.create(product=item_front, layout_category="Parkett vorne")
    event.seat_category_mappings.create(product=item_front, layout_category="Balkon vorne")
    event.seat_category_mappings.create(product=item_middle, layout_category="Bakkon hinten")
    event.seat_category_mappings.create(product=item_middle, layout_category="Parkett mitte")
    event.seat_category_mappings.create(product=item_back, layout_category="Parkett hinten")
    quota_tickets = event.quotas.create(name='Tickets', size=None)
    quota_tickets.items.add(item_front)
    quota_tickets.items.add(item_middle)
    quota_tickets.items.add(item_back)
    quota_tickets.variations.add(*item_back.variations.all())
    quota_tickets.variations.add(*item_front.variations.all())
    quota_tickets.variations.add(*item_middle.variations.all())
    event.name = _('Heidelberg Orchestra in Concert')
    event.location = _('Concert Hall\nMozart Street 5\nHeidelberg')
    event.date_to = None
    event.date_from = event.date_from.replace(hour=19)
    event.seating_plan = seating_plan
    event.plugins += ',pretix_seating'
    event.save()

    value = open(os.path.join(os.path.dirname(__file__), "../../assets/concert_header.jpg"), "rb")
    newname = default_storage.save('logo.jpg', ContentFile(value.read()))
    event.settings.logo_image = 'file://' + newname
    event.settings.logo_image_large = True
    event.settings.primary_color = '#ed0808'
    event.settings.theme_color_background = '#821f1f'
    event.settings.primary_font = 'Montserrat'

    generate_seats(event, None, event.seating_plan, {
        m.layout_category: m.product
        for m in event.seat_category_mappings.select_related('product').filter(subevent=None)
    })
    previous_blocked = True
    for s in event.seats.all():
        if not s.seat_guid.startswith("1-"):
            if random.random() > (0.3 if previous_blocked else 0.9):
                s.blocked = True
                s.save()
        previous_blocked = s.blocked
    regenerate_css.apply_async(args=(event.pk,))
    return event


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_seating' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_seating_settings(live_server, organizer, event, logged_in_client, seating_event):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/seating'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/seating/mapping.png')


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_seating' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_selection(live_server, logged_in_client, organizer, event, seating_event):
    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_elements_by_css_selector("svg circle.seat")[10].click()
    logged_in_client.find_elements_by_css_selector("svg circle.seat")[11].click()
    logged_in_client.find_elements_by_css_selector("svg circle.seat")[12].click()
    logged_in_client.find_elements_by_css_selector("select.frontrow-selected-item-variation-selection")[2].click()
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/seating/checkout.png')
