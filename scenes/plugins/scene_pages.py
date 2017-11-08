import pytest
import time
from django.conf import settings
from i18nfield.strings import LazyI18nString
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from ..utils import screenshot


@pytest.fixture
def page_tos(event):
    from pretix_pages.models import Page

    return Page.objects.create(
        event=event,
        slug="tos",
        title=LazyI18nString({'de': 'AGB', 'en': 'Terms of Service'}),
        require_confirmation=True,
        link_in_footer=True,
        link_on_frontpage=True,
        text='Tickets are non-refundable.<br><br>Be excellent to each other.<br><br>Thank you!'
    )


@pytest.fixture
def page_faq(event):
    from pretix_pages.models import Page

    return Page.objects.create(
        event=event,
        slug="faq",
        title=LazyI18nString({'de': 'Häufige Fragen', 'en': 'FAQ'}),
        require_confirmation=False,
        link_in_footer=True,
        link_on_frontpage=True,
        text=LazyI18nString({
            'en': '<h3>What is this?</h3><p>A screenshot.</p>'
        })
    )


@pytest.mark.django_db
@pytest.mark.skipif(
    'pretix_pages' not in settings.INSTALLED_APPS,
    reason='Plugin not installed.'
)
def shot_pages(live_server, organizer, event, logged_in_client, page_faq, page_tos):
    event.plugins += ',pretix_pages'
    event.save()

    logged_in_client.get(live_server.url + '/control/event/{}/{}/pages'.format(
        organizer.slug, event.slug
    ))
    screenshot(logged_in_client, 'plugins/pages/list.png')
    logged_in_client.get(live_server.url + '/control/event/{}/{}/pages/{}/'.format(
        organizer.slug, event.slug, page_tos.pk
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ql-formats"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/pages/edit.png')
    logged_in_client.get(live_server.url + '/{}/{}/page/{}/'.format(
        organizer.slug, event.slug, page_faq.slug
    ))
    screenshot(logged_in_client, 'plugins/pages/frontend.png')
