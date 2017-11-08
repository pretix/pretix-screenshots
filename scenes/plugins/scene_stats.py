import random
import time
from datetime import timedelta
from decimal import Decimal

from django.utils.timezone import now
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from pretix.base.models import Order
from ..utils import screenshot


def shot_statistics(live_server, organizer, event, logged_in_client):
    event.plugins += ',pretix.plugins.statistics'
    event.save()

    eb = event.items.create(name='Early-bird ticket', default_price=23, admission=True)
    regular = event.items.create(name='Regular ticket', default_price=26, admission=True)
    for day in range(30):
        d = now() - timedelta(days=day)
        num = max(0, random.randint(25, 45) - day)
        for l in range(num):
            order = event.orders.create(
                status=Order.STATUS_PAID,
                email='admin@localhost',
                expires=now(),
                datetime=d,
                payment_date=d,
                total=Decimal("23"),
                payment_provider='banktransfer',
                locale='en'
            )
            if day > 15:
                order.positions.create(
                    item=eb, price=Decimal('23.00')
                )
            else:
                order.positions.create(
                    item=regular, price=Decimal('26.00')
                )

    logged_in_client.get(live_server.url + '/control/event/{}/{}/statistics/'.format(
        organizer.slug, event.slug
    ))
    WebDriverWait(logged_in_client, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#obp_chart svg"))
    )
    time.sleep(.5)
    screenshot(logged_in_client, 'plugins/statistics/view.png')
