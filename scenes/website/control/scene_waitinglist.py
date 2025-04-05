import random

import faker
import pytest
from django.utils.translation import gettext as _
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
def waitinglistentries(event, items):
    fake = faker.Faker()
    for i in range(42):
        event.waitinglistentries.create(
            item=random.choice(items),
            created=fake.date_time_between(start_date="-14d", end_date="now", tzinfo=None),
            email=fake.email()
        )


@pytest.mark.django_db
def shot_waiting_list_admin(live_server, organizer, event, logged_in_client, waitinglistentries):
    event.live = True
    event.settings.waiting_list_enabled = True
    event.settings.waiting_list_auto = True
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/waitinglist/'.format(
        organizer.slug, event.slug
    ))
    logged_in_client.find_element(By.CSS_SELECTOR, ".table-condensed")
    screenshot(logged_in_client, 'website/control/waiting_list_admin.png')
