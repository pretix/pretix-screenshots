import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_organizer_list(live_server, organizer, logged_in_client):
    logged_in_client.get(live_server.url + '/control/organizers/')
    screenshot(logged_in_client, 'screens/organizer/organizer_list.png')
