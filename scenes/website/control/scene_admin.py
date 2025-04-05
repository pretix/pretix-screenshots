import pytest
from django.conf import settings

from ...utils import screenshot


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_reports' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_reports(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/reports/orderpositions/')
    screenshot(logged_in_client, 'website/control/reports.png')


@pytest.mark.django_db
def shot_organizer_team_edit(live_server, organizer, event, admin_team, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/team/{}/edit'.format(organizer.slug, admin_team.pk))
    screenshot(logged_in_client, 'website/control/team_edit.png')


@pytest.mark.django_db
def shot_notifications(live_server, organizer, event, admin_team, logged_in_client):
    logged_in_client.get(live_server.url + '/control/settings/notifications/')
    screenshot(logged_in_client, 'website/control/notifications.png')
