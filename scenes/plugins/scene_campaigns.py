import random
import time
from datetime import timedelta

import pytest
from decimal import Decimal
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pretix.base.models import Order
from ..utils import screenshot


@pytest.fixture
def campaign_web(event):
    from pretix_campaigns.models import Campaign

    return Campaign.objects.create(
        event=event,
        description=_('Event website'),
    )


@pytest.fixture
def campaign_twitter(event):
    from pretix_campaigns.models import Campaign

    return Campaign.objects.create(
        event=event,
        description='Twitter',
    )


@pytest.fixture
def orders(event, campaign_twitter, campaign_web):
    eb = event.items.create(name=_('Early-bird ticket'), default_price=23, admission=True)
    regular = event.items.create(name=_('Regular ticket'), default_price=26, admission=True)
    for day in range(30):
        d = now() - timedelta(days=day)
        num = max(0, random.randint(25, 45) - day)
        for l in range(num):
            order = event.orders.create(
                status=Order.STATUS_PAID,
                email='admin@localhost',
                expires=now(),
                datetime=d,
                payment_date=d,
                total=Decimal("23"),
                payment_provider='banktransfer',
                locale='en'
            )
            random.choice([campaign_twitter, campaign_web, campaign_web]).orders.add(order)
            if day > 15:
                order.positions.create(
                    item=eb, price=Decimal('23.00'),
                )
            else:
                order.positions.create(
                    item=regular, price=Decimal('26.00')
                )


@pytest.fixture
def clicks(event, campaign_twitter, campaign_web):
    from pretix_campaigns.models import CampaignClick

    for day in range(30):
        d = now() - timedelta(days=day)
        CampaignClick.objects.create(
            campaign=campaign_web,
            date=d.date(),
            count=random.randint(0, 100)
        )
        CampaignClick.objects.create(
            campaign=campaign_twitter,
            date=d.date(),
            count=random.randint(0, 50)
        )


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_campaigns' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_campaign(live_server, organizer, event, logged_in_client, campaign_web, campaign_twitter, orders, clicks):
    event.plugins += ',pretix_campaigns'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/campaigns/'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/campaigns/list.png')
    logged_in_client.get(live_server.url + '/control/event/{}/{}/campaigns/{}/edit'.format(
        organizer.slug, event.slug, campaign_twitter.code
    ))
    screenshot(logged_in_client, 'plugins/campaigns/edit.png')

    logged_in_client.get(live_server.url + '/control/event/{}/{}/campaigns/{}/'.format(
        organizer.slug, event.slug, campaign_twitter.code
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cbd_chart svg"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/campaigns/stats.png')
