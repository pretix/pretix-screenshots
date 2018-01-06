import datetime
import pytest
import pytz
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from ...utils import screenshot


@pytest.fixture
def subevents(event):
    event.has_subevents = True
    event.name = _("Workshop Tour")
    event.save()
    se1 = event.subevents.create(
        name="Hamburg",
        active=True,
        date_from=datetime.datetime((now().year + 1), 7, 31, 9, 0, 0, tzinfo=pytz.UTC),
    )
    se1.quotas.create(event=event, name=_("Main quota"), size=20)
    se2 = event.subevents.create(
        name="Berlin",
        active=True,
        date_from=datetime.datetime((now().year + 1), 8, 2, 9, 0, 0, tzinfo=pytz.UTC),
    )
    se2.quotas.create(event=event, name=_("Main quota"), size=20)
    se3 = event.subevents.create(
        name=_("Munich"),
        active=True,
        date_from=datetime.datetime((now().year + 1), 8, 6, 9, 0, 0, tzinfo=pytz.UTC),
    )
    se3.quotas.create(event=event, name=_("Main quota"), size=20)
    return se1, se2, se3


@pytest.mark.django_db
def shot_list(live_server, organizer, event, subevents, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/subevents/'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/subevent_list.png')


@pytest.mark.django_db
def shot_detail(live_server, organizer, event, subevents, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/subevents/{}/'.format(
        organizer.slug, event.slug, subevents[0].pk
    ))
    screenshot(logged_in_client, 'event/subevent_detail.png')


@pytest.mark.django_db
def shot_create(live_server, organizer, event, subevents, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/subevents/add'.format(
        organizer.slug, event.slug,
    ))
    screenshot(logged_in_client, 'event/subevent_create.png')
