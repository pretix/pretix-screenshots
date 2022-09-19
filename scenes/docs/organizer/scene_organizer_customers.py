from decimal import Decimal

import faker
import pytest
from django.utils.timezone import now

from django.utils.translation import gettext as _

from pretix.base.models import Order
from ...utils import screenshot


@pytest.mark.django_db
def shot_customer_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/edit'.format(organizer.slug))
    logged_in_client.find_element_by_css_selector("a[href='#tab-0-3']").click()
    screenshot(logged_in_client, 'organizer/edit_customer.png')

    logged_in_client.get(live_server.url + '/control/organizer/{}/ssoclient/add'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/customer_ssoclient_add.png')

    logged_in_client.get(live_server.url + '/control/organizer/{}/ssoprovider/add'.format(organizer.slug))
    logged_in_client.find_element_by_css_selector("#id_method_0").click()
    screenshot(logged_in_client, 'organizer/customer_ssoprovider_add.png')


@pytest.mark.django_db
def shot_customer_list(live_server, organizer, event, logged_in_client):
    fake = faker.Faker()
    for i in range(20):
        organizer.customers.create(email=fake.email(), name_parts={'_legacy': fake.name()})

    logged_in_client.get(live_server.url + '/control/organizer/{}/customers'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/customers.png')


@pytest.mark.django_db
def shot_customer_detail(live_server, organizer, event, logged_in_client):
    fake = faker.Faker()
    c = organizer.customers.create(email=fake.email(), name_parts={'_legacy': fake.name()})
    for l in range(2):
        event.orders.create(
            status=Order.STATUS_PENDING,
            email='admin@localhost',
            expires=now(),
            datetime=now(),
            total=Decimal("23"),
            locale='en',
            customer=c,
        )

    logged_in_client.get(live_server.url + '/control/organizer/{}/customer/{}/'.format(organizer.slug, c.identifier))
    screenshot(logged_in_client, 'organizer/customer.png')

    logged_in_client.get(live_server.url + '/control/organizer/{}/customer/{}/edit'.format(organizer.slug, c.identifier))
    screenshot(logged_in_client, 'organizer/customer_edit.png')
