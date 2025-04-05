import json
import random
import time
from datetime import timedelta
from decimal import Decimal

import pytest
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import gettext as _
from pretix.base.models import Order, OrderPayment
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ..utils import screenshot


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_stretchgoals' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_stretchgoals(live_server, organizer, event, logged_in_client):
    event.plugins += ',pretix_stretchgoals'
    event.save()

    eb = event.items.create(name=_('Early-bird ticket'), default_price=23, admission=True)
    regular = event.items.create(name=_('Regular ticket'), default_price=26, admission=True)
    event.settings.stretchgoals_items = '{},{}'.format(eb.pk, regular.pk)
    event.settings.stretchgoals_chart_averages = True
    event.settings.stretchgoals_chart_totals = True
    event.settings.stretchgoals_is_public = True
    event.settings.stretchgoals_goals = json.dumps([
        {
            'name': _('Break-even'),
            'total': 10000,
            'amount': 435,
            'description': ''
        },
        {
            'name': _('We can have a party'),
            'total': 20000,
            'amount': 435,
            'description': ''
        }
    ])
    for day in range(30):
        d = now() - timedelta(days=day)
        order = event.orders.create(
            status=Order.STATUS_PAID,
            email='admin@localhost',
            expires=now(),
            datetime=d,
            total=Decimal("23"),
            locale='en'
        )
        order.payments.create(
            provider='banktransfer',
            amount=order.total,
            payment_date=d,
            state=OrderPayment.PAYMENT_STATE_CONFIRMED
        )
        num = max(0, random.randint(25, 45) - day)
        for l in range(num):
            if day > 15:
                order.positions.create(
                    item=regular, price=Decimal('23.00')
                )
            else:
                order.positions.create(
                    item=regular, price=Decimal('26.00')
                )

    logged_in_client.get(live_server.url + '/control/event/{}/{}/stretchgoals/settings/'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/stretchgoals/settings.png')
    logged_in_client.get(live_server.url + '/control/event/{}/{}/stretchgoals/'.format(
        organizer.slug, event.slug
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#avg_chart svg"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/stretchgoals/backend.png')

    logged_in_client.get(live_server.url + '/{}/{}/stats/'.format(
        organizer.slug, event.slug
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#avg_chart svg"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/stretchgoals/frontend.png')
