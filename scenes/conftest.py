import pytest
from selenium.webdriver.support.wait import WebDriverWait

from pretix.base.models import Organizer, User


@pytest.fixture
def user():
    return User.objects.create_user('john@example.org', 'john', fullname='John Doe')


@pytest.fixture
def organizer(user):
    o = Organizer.objects.create(name="Awesome Event Corporation", slug="aec")
    t = o.teams.create(name="Admin team")
    t.members.add(user)
    return o


@pytest.fixture
def logged_in_client(live_server, selenium, user):
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