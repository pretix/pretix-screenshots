import datetime
import os
from decimal import Decimal
from selenium.webdriver.common.by import By

import pytest
import pytz
from django.test import utils
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django_scopes import scopes_disabled
from i18nfield.strings import LazyI18nString

from pretix.base.i18n import language
from pretix.base.models import Organizer, User
from pretix.base.settings import GlobalSettingsObject


@pytest.yield_fixture(params=["en", "de"], autouse=True)
def locale(request):
    with language(request.param), scopes_disabled():
        yield request.param


@pytest.fixture
def user(locale):
    return User.objects.create_user('john@example.org', 'john', fullname=_('John Doe'), locale=locale)


@pytest.fixture
def webhook(organizer):
    wh = organizer.webhooks.create(
        enabled=True,
        target_url='https://example.com/webhookendpoint/',
        all_events=True
    )
    wh.listeners.create(action_type='pretix.event.order.placed')
    wh.listeners.create(action_type='pretix.event.order.paid')
    return wh


@pytest.fixture
def admin_team(organizer, user):
    t = organizer.teams.create(name=_("Admin team"), all_events=True, can_change_organizer_settings=True,
                               can_change_event_settings=True, can_change_items=True, can_change_teams=True,
                               can_create_events=True, can_view_orders=True, can_change_orders=True,
                               can_view_vouchers=True, can_change_vouchers=True, can_manage_customers=True,
                               can_manage_gift_cards=True)
    t.members.add(user)
    return t


@pytest.fixture
def organizer(user, locale):
    o = Organizer.objects.create(name=_("Awesome Event Corporation"), slug="aec")
    return o


@pytest.fixture
def event(organizer, locale):
    e = organizer.events.create(
        name=_("25th International Ticketing Conference"),
        slug="ydc",
        date_from=datetime.datetime((now().year + 1), 7, 31, 9, 0, 0, tzinfo=pytz.UTC),
        date_to=datetime.datetime((now().year + 1), 8, 2, 16, 0, 0, tzinfo=pytz.UTC),
        live=True,
        currency='EUR',
        plugins='pretix.plugins.banktransfer,pretix.plugins.ticketoutputpdf',
        is_public=True,
        location=_('Heidelberg, Germany'),
    )
    if locale in ['en', 'de']:
        e.settings.locales = ['en', 'de']
    else:
        e.settings.locales = ['en', locale]
    e.settings.language = locale
    return e


@pytest.fixture
def tax_rule(event):
    return event.tax_rules.create(name=LazyI18nString({'en': 'VAT', 'de': 'MwSt'}), rate=Decimal('19.00'))


@pytest.fixture
def var(organizer, settings):
    try:
        from pretixeu.billing.models import BrandingPartner, OrganizerProfile
        import pretixeu
    except ImportError:
        pytest.skip("pretixeu not installed")
    bp = BrandingPartner(
        name="ticketshop.live",
        public_name="ticketshop.live",
        public_url="https://ticketshop.live",
        support_email="support@ticketshop.live",
    )
    bp.logo.save("logo.png", open(os.path.join(os.path.dirname(__file__), "../assets/ticketshoplive_logo.png"), "rb"))
    bp.save()
    p = OrganizerProfile.objects.get_or_create(organizer=organizer)[0]
    p.branding_partner = bp
    p.save()
    return bp


@pytest.fixture
def client(live_server, selenium, user, admin_team, locale):
    selenium.implicitly_wait(10)
    return selenium


@pytest.fixture
def logged_in_client(live_server, selenium, user, admin_team, locale):
    selenium.get(live_server.url + '/control/login')
    selenium.implicitly_wait(10)

    selenium.find_element(By.CSS_SELECTOR, "form input[name=email]").send_keys(user.email)
    selenium.find_element(By.CSS_SELECTOR, "form input[name=password]").send_keys('john')
    selenium.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
    return selenium


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1366x768')
    return chrome_options


@pytest.fixture(autouse=True)
def noupdatewarn():
    gs = GlobalSettingsObject()
    gs.settings.update_check_ack = True


utils.setup_databases = scopes_disabled()(utils.setup_databases)
