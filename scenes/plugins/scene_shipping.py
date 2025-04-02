import pytest
import time
from selenium.webdriver.common.by import By

from decimal import Decimal
from django.conf import settings
from django.utils.translation import gettext as _


from ..utils import screenshot


@pytest.fixture
def shipping_method_letter(event, tax_rule):
    from pretix_shipping.models import ShippingMethod

    return ShippingMethod.objects.create(
        event=event,
        active=True,
        method_type='ship',
        name=_('Postal Service'),
        description=_('Your ticket will be sent to your home.'),
        tax_rule=tax_rule,
        price=Decimal('2.50')
    )


@pytest.fixture
def shipping_method_online(event):
    from pretix_shipping.models import ShippingMethod

    return ShippingMethod.objects.create(
        event=event,
        active=True,
        method_type='online',
        price=0,
        name=_('Print at home'),
        description=_('You can download your ticket right away.'),
    )


@pytest.fixture
def cart(organizer, event, tax_rule, live_server, logged_in_client):
    quota_tickets = event.quotas.create(name='Tickets', size=5)
    ticket = event.items.create(
        name=_('Early-bird ticket'), default_price=23, admission=True,
        tax_rule=tax_rule
    )
    quota_tickets.items.add(ticket)

    logged_in_client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug,
    ))
    logged_in_client.find_element_by_id("btn-add-to-cart").click()
    logged_in_client.find_element(By.CSS_SELECTOR, ".cart-row")
    logged_in_client.get(live_server.url + '/{}/{}/checkout/start'.format(
        organizer.slug, event.slug,
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, "input[name='email']").send_keys("support@pretix.eu")
    logged_in_client.find_element(By.CSS_SELECTOR, ".btn-primary").click()


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_shipping' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_shipping_settings(live_server, organizer, event, logged_in_client, shipping_method_letter):
    event.plugins += ',pretix_shipping'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/shipping/'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/shipping/list.png')
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/shipping/{}/'.format(
        organizer.slug, event.slug, shipping_method_letter.pk
    ))
    screenshot(logged_in_client, 'plugins/shipping/edit.png')


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_shipping' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_shipping_checkout(live_server, organizer, event, logged_in_client, shipping_method_letter, shipping_method_online, cart):
    event.plugins += ',pretix_shipping'
    event.save()

    logged_in_client.get(live_server.url + '/{}/{}/checkout/shipping'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, "input[name='shipping_method']").click()
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/shipping/checkout.png')
