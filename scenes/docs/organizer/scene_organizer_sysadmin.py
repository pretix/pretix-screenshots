import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_organizer_edit(live_server, organizer, event, user, logged_in_client):
    user.is_staff = True
    user.save()
    logged_in_client.get(live_server.url + '/control/')
    logged_in_client.find_element_by_css_selector("#button-sudo").click()
    logged_in_client.find_element_by_css_selector("a.danger")
    logged_in_client.get(live_server.url + '/control/organizer/{}/edit'.format(organizer.slug))
    screenshot(logged_in_client, 'organizer/edit_sysadmin.png')
