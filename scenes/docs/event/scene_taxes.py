import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_tax_list(live_server, organizer, event, tax_rule, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/tax/'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/tax_list.png')


@pytest.mark.django_db
def shot_tax_detail(live_server, organizer, event, tax_rule, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/tax/{}/'.format(
        organizer.slug, event.slug, tax_rule.pk
    ))
    screenshot(logged_in_client, 'event/tax_detail.png')
