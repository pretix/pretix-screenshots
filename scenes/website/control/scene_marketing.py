import random
import time
from datetime import timedelta

import pytest
from selenium.webdriver.common.by import By
from decimal import Decimal

from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.timezone import now
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pretix.base.models import Order, OrderPayment
from ...utils import screenshot


@pytest.mark.django_db
def shot_voucher_create(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/vouchers/add'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, "#id_code")
    Select(logged_in_client.find_element(By.NAME, 'price_mode')).select_by_value("percent")
    logged_in_client.find_element(By.CSS_SELECTOR, "#id_value").send_keys("25")

    screenshot(logged_in_client, 'website/control/voucher_create.png')


@pytest.mark.django_db
def shot_sendmail(live_server, organizer, event, logged_in_client):
    event.plugins += ",pretix.plugins.sendmail"
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/sendmail/'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, "#id_subject_0")
    screenshot(logged_in_client, 'website/control/sendmail.png')


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
                total=Decimal("23"),
                locale='en'
            )
            order.payments.create(
                state=OrderPayment.PAYMENT_STATE_CONFIRMED,
                provider="banktransfer",
                payment_date=d,
                amount=order.total
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
    screenshot(logged_in_client, 'website/control/campaigns_list.png')
    logged_in_client.get(live_server.url + '/control/event/{}/{}/campaigns/{}/'.format(
        organizer.slug, event.slug, campaign_twitter.code
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cbd_chart svg"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'website/control/campaigns_detail.png')


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_campaigns' not in settings.INSTALLED_APPS or 'pretixeu.billing' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_campaign_var(live_server, organizer, event, logged_in_client, campaign_web, campaign_twitter, orders, clicks,
                      var):
    event.plugins += ',pretix_campaigns'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/campaigns/{}/'.format(
        organizer.slug, event.slug, campaign_twitter.code
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#cbd_chart svg"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'website/control/campaigns_detail_var.png')
