import pytest
from selenium.webdriver.common.by import By
import time
from django.utils.translation import gettext as _

from ...utils import screenshot


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
    wc1 = event.items.create(name=_('Workshop session: Digital future'), default_price=12, active=True, category=wc, tax_rule=tax_rule)
    wc2 = event.items.create(name=_('Workshop session: Analog future'), default_price=12, active=True, category=wc, tax_rule=tax_rule)
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


@pytest.mark.django_db
def shot_shop_frontpage(live_server, organizer, event, items, logged_in_client):
    client = logged_in_client
    event.live = True
    event.save()
    event.settings.locales = ['en', 'de']
    event.settings.waiting_list_enabled = True
    event.settings.waiting_list_auto = True

    client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    client.find_element(By.CSS_SELECTOR, "button[data-toggle=variations]").click()
    time.sleep(1)
    client.find_element(By.CSS_SELECTOR, ".product-description").click()
    screenshot(client, 'website/frontend/shop_frontpage.png')


@pytest.mark.django_db
def shot_shop_checkout_steps(live_server, organizer, event, items, logged_in_client):
    client = logged_in_client
    event.live = True
    event.plugins += ",pretix.plugins.stripe,pretix.plugins.paypal"
    event.save()
    event.settings.locales = ['en', 'de']
    event.settings.attendee_names_asked = True
    event.settings.payment_banktransfer__enabled = True
    event.settings.payment_paypal__enabled = True
    event.settings.payment_stripe__enabled = True
    event.settings.payment_stripe_method_cc = True
    event.settings.payment_stripe_method_giropay = True
    event.settings.payment_stripe_method_sofort = True
    #event.settings.payment_paypal__fee_abs = 0.34
    #event.settings.payment_paypal__fee_percent = 1.4

    # Index
    client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    client.find_element(By.CSS_SELECTOR, "input[name=item_{}]".format(items[0].pk)).send_keys('1')
    client.find_element(By.CSS_SELECTOR, "#btn-add-to-cart").click()

    # Cart
    client.find_element(By.CSS_SELECTOR, ".cart")
    screenshot(client, 'website/frontend/shop_addons.png')
    client.find_element(By.CSS_SELECTOR, ".cart .btn-primary").click()

    # Addons
    client.find_element(By.CSS_SELECTOR, ".checkout-flow")
    screenshot(client, 'website/frontend/shop_addons.png')
    client.find_element(By.CSS_SELECTOR, ".btn-primary").click()

    # Questions
    client.find_element(By.CSS_SELECTOR, "#id_email")
    screenshot(client, 'website/frontend/shop_questions.png')
    client.find_element(By.CSS_SELECTOR, "#id_email").send_keys('support@pretix.eu')
    client.find_element(By.CSS_SELECTOR, ".btn-primary").click()

    # Payment
    client.find_element(By.CSS_SELECTOR, "#payment_accordion")
    screenshot(client, 'website/frontend/shop_payment.png')


@pytest.mark.django_db
def shot_shop_checkout_customer_step(live_server, organizer, event, items, logged_in_client):
    client = logged_in_client
    event.live = True
    event.settings.locales = ['en', 'de']
    event.settings.attendee_names_asked = True
    event.settings.payment_banktransfer__enabled = True
    event.organizer.settings.customer_accounts = True

    # Index
    client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    client.find_element(By.CSS_SELECTOR, "input[name=item_{}]".format(items[0].pk)).send_keys('1')
    client.find_element(By.CSS_SELECTOR, "#btn-add-to-cart").click()

    # Cart
    client.find_element(By.CSS_SELECTOR, ".cart")

    client.get(live_server.url + '/{}/{}/checkout/customer/'.format(
        organizer.slug, event.slug
    ))
    # Login
    client.find_element(By.CSS_SELECTOR, "#id_login-email")
    client.find_element(By.CSS_SELECTOR, "[data-target='#customer_login']").click()
    screenshot(client, 'website/frontend/shop_customer.png')
