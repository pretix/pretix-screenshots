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


@pytest.mark.django_db
def shot_plugin_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/plugins'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/settings_plugins.png')


@pytest.mark.django_db
def shot_display_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/display'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/settings_display.png')


@pytest.mark.django_db
def shot_tickets_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/tickets'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/settings_tickets.png')


@pytest.mark.django_db
def shot_email_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/email'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/settings_email.png')


@pytest.mark.django_db
def shot_invoice_settings(live_server, organizer, event, logged_in_client):
    logged_in_client.get(live_server.url + '/control/event/{}/{}/settings/invoice'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'event/settings_invoice.png')
