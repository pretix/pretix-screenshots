import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_organizer_list(live_server, organizer, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizers/')
    screenshot(logged_in_client, 'organizer/list.png')


@pytest.mark.django_db
def shot_organizer_event_list(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/event_list.png')


@pytest.mark.django_db
def shot_organizer_edit(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/edit'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/edit.png')


@pytest.mark.django_db
def shot_organizer_team_list(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/teams'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/team_list.png')


@pytest.mark.django_db
def shot_organizer_team_detail(live_server, organizer, event, admin_team, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/team/{}/'.format(organizer.slug, admin_team.pk))
    screenshot(logged_in_client, 'organizer/team_detail.png')


@pytest.mark.django_db
def shot_organizer_team_edit(live_server, organizer, event, admin_team, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/team/{}/edit'.format(organizer.slug, admin_team.pk))
    screenshot(logged_in_client, 'organizer/team_edit.png')


@pytest.mark.django_db
def shot_organizer_webhook_list(live_server, organizer, event, webhook, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/webhooks'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/webhook_list.png')


@pytest.mark.django_db
def shot_organizer_webhook_edit(live_server, organizer, event, webhook, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizer/{}/webhook/{}/edit'.format(organizer.slug, webhook.pk))
    screenshot(logged_in_client, 'organizer/webhook_edit.png')
