import pytest
import time

from django.conf import settings
from django.utils.translation import ugettext as _

from ...utils import screenshot


@pytest.fixture
def items(event, tax_rule):
    i1 = event.items.create(name=_('Business Ticket'), default_price=400, admission=True, tax_rule=tax_rule,
                            active=True, position=2)
    i2 = event.items.create(name=_('Individual Ticket'), default_price=250, admission=True, tax_rule=tax_rule,
                            active=True, position=1)
    i3 = event.items.create(name=_('VIP Ticket'), default_price=600, admission=True, tax_rule=tax_rule,
                            active=True, position=3)

    q1 = event.quotas.create(name=_('Available'), size=100)
    q1.items.add(i1)
    q1.items.add(i2)
    q2 = event.quotas.create(name=_('Unavailable'), size=0)
    q2.items.add(i3)
    return [i1, i2, i3]


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretixeu.billing' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_shop_frontpage_var(live_server, organizer, var, event, items, logged_in_client):
    client = logged_in_client
    event.live = True
    event.save()
    event.settings.locales = ['en', 'de']
    event.settings.waiting_list_enabled = True
    event.settings.waiting_list_auto = True

    client.get(live_server.url + '/{}/{}/'.format(
        organizer.slug, event.slug
    ))
    screenshot(client, 'website/frontend/shop_frontpage_var.png')
