import random
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils.timezone import now
from django.utils.translation import gettext as _
from pretix.base.models import Order
from selenium.webdriver.common.by import By

from ...utils import screenshot


@pytest.fixture
def items(event, tax_rule):
    i1 = event.items.create(name=_('Business Ticket'), default_price=400, admission=True, tax_rule=tax_rule,
                            active=True, position=2)
    i2 = event.items.create(name=_('VIP Ticket'), default_price=600, admission=True, tax_rule=tax_rule,
                            active=True, position=3)

    q1 = event.quotas.create(name='Available', size=7)
    q1.items.add(i1)
    q2 = event.quotas.create(name='Available', size=3)
    q2.items.add(i2)
    return i1, i2


@pytest.fixture
def list_all(event, items):
    return event.checkin_lists.create(
        name=_('General admission'),
        all_products=True,
    )


@pytest.fixture
def list_vip(event, items):
    l = event.checkin_lists.create(
        name=_('VIP Lounge'),
        all_products=False,
    )
    l.limit_products.add(items[1])
    return l


@pytest.fixture
def data(event, items, list_all, list_vip):
    for l in range(334):
        d = now() - timedelta(days=5)
        order = event.orders.create(
            status=Order.STATUS_PAID,
            email='admin@localhost',
            expires=now(),
            datetime=d,
            total=Decimal("23"),
            locale='en'
        )
        if random.randrange(0, 10) < 3:
            p = order.positions.create(
                item=items[1], price=Decimal('600.00'),
            )
            if random.randrange(0, 10) < 5:
                p.checkins.create(datetime=d, list=list_all)
            if random.randrange(0, 10) < 3:
                p.checkins.create(datetime=d, list=list_vip)
        else:
            p = order.positions.create(
                item=items[0], price=Decimal('400.00')
            )
            if random.randrange(0, 10) < 6:
                p.checkins.create(datetime=d, list=list_all)


@pytest.mark.django_db
def shot_waiting_list_admin(live_server, organizer, event, logged_in_client, data):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/checkinlists/'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, ".table")
    screenshot(logged_in_client, 'website/control/checkinlist_admin.png')
