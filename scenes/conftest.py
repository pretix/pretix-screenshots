import datetime
from decimal import Decimal

import pytest
import pytz
from django.utils.timezone import now
from i18nfield.strings import LazyI18nString

from pretix.base.models import Organizer, User


@pytest.fixture
def user():
    return User.objects.create_user('john@example.org', 'john', fullname='John Doe')


@pytest.fixture
def admin_team(organizer, user):
    t = organizer.teams.create(name="Admin team", all_events=True, can_change_organizer_settings=True,
                               can_change_event_settings=True, can_change_items=True, can_change_teams=True,
                               can_create_events=True, can_view_orders=True, can_change_orders=True,
                               can_view_vouchers=True, can_change_vouchers=True)
    t.members.add(user)
    return t


@pytest.fixture
def organizer(user):
    o = Organizer.objects.create(name="Awesome Event Corporation", slug="aec")
    return o


@pytest.fixture
def event(organizer):
    e = organizer.events.create(
        name="Yearly Demo Conference",
        slug="ydc",
        date_from=datetime.datetime((now().year + 1), 7, 31, 9, 0, 0, tzinfo=pytz.UTC),
        date_to=datetime.datetime((now().year + 1), 8, 2, 16, 0, 0, tzinfo=pytz.UTC),
        live=True,
        currency='EUR',
        is_public=True,
        location='Heidelberg, Germany',
    )
    return e


@pytest.fixture
def tax_rule(event):
    return event.tax_rules.create(name=LazyI18nString({'en': 'VAT', 'de': 'MwSt'}), rate=Decimal('19.00'))


@pytest.fixture
def logged_in_client(live_server, selenium, user, admin_team):
    selenium.get(live_server.url + '/control/login')
    selenium.implicitly_wait(10)

    selenium.find_element_by_css_selector("form input[name=email]").send_keys(user.email)
    selenium.find_element_by_css_selector("form input[name=password]").send_keys('john')
    selenium.find_element_by_css_selector("form button[type=submit]").click()
    return selenium


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1024x768')
    return chrome_options
