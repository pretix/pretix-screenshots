import pytest
import time

from decimal import Decimal
from django.conf import settings
from django.utils.translation import ugettext as _


from ..utils import screenshot


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
    wc1 = event.items.create(name=_('Workshop session: Digital future'), default_price=12, active=True, category=wc)
    wc2 = event.items.create(name=_('Workshop session: Analog future'), default_price=12, active=True, category=wc)
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


@pytest.fixture
def reseller(event, user):
    from pretix_resellers.models import Reseller

    r = Reseller.objects.create(
        id='DEHDCS',
        name='The Corner Store',
        address='Foo'
    )
    r.organizers.add(event.organizer)
    r.users.add(user)
    return r


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_resellers' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_index(live_server, organizer, event, logged_in_client, reseller):
    event.plugins += ',pretix_resellers'
    event.save()

    logged_in_client.get(live_server.url + '/reseller/{}/'.format(
        reseller.pk
    ))
    screenshot(logged_in_client, 'plugins/resellers/index.png')


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_resellers' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_event_selection(live_server, organizer, event, logged_in_client, reseller):
    event.plugins += ',pretix_resellers'
    event.save()

    logged_in_client.get(live_server.url + '/reseller/{}/events'.format(
        reseller.pk
    ))
    screenshot(logged_in_client, 'plugins/resellers/events.png')


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_resellers' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_event_detail(live_server, organizer, event, logged_in_client, reseller, items):
    event.plugins += ',pretix_resellers'
    event.save()

    logged_in_client.get(live_server.url + '/reseller/{}/events/{}/{}/'.format(
        reseller.pk, organizer.slug, event.slug
    ))
    time.sleep(5)
    screenshot(logged_in_client, 'plugins/resellers/event.png')
