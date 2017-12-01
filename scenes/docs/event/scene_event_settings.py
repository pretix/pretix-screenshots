import pytest

from ...utils import screenshot


@pytest.mark.django_db
def shot_widget_creator(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/widget'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/widget_form.png')


@pytest.mark.django_db
def shot_payment_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/payment'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/settings_payment.png')
