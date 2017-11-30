import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_organizer_edit(live_server, organizer, event, user, logged_in_client):
    user.is_superuser = True
    user.save()
    logged_in_client.get(live_server.url + '/control/organizer/{}/edit'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/edit_sysadmin.png')
