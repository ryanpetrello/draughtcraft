from draughtcraft.templates.helpers     import (stamp, format_date, format_age,
                                                format_percentage)
from unittest                           import TestCase
from datetime                           import datetime, timedelta

class TestHelpers(TestCase):

    def test_stamp(self):
        assert stamp('/javascript/foo.js') == '/javascript/foo.js?XYZ'

    def test_format_percentage(self):
        assert format_percentage(0) == '0%'
        assert format_percentage(0.00) == '0%'
        assert format_percentage(0.01) == '1%'
        assert format_percentage(0.011) == '1.1%'
        assert format_percentage(0.0125) == '1.25%'
        assert format_percentage(0.012549) == '1.25%'
        assert format_percentage(0.01255) == '1.26%'
        assert format_percentage(1.00) == '100%'

        assert format_percentage(0.012549, digits=3) == '1.255%'
        assert format_percentage(0.01255, digits=3) == '1.255%'

        assert format_percentage(0, symbol=False) == '0'
        assert format_percentage(0.00, symbol=False) == '0'
        assert format_percentage(0.01, symbol=False) == '1'
        assert format_percentage(0.011, symbol=False) == '1.1'
        assert format_percentage(0.0125, symbol=False) == '1.25'
        assert format_percentage(0.012549, symbol=False) == '1.25'
        assert format_percentage(0.01255, symbol=False) == '1.26'
        assert format_percentage(1.00, symbol=False) == '100'

    def test_format_date(self):
        assert format_date(datetime(2011, 5, 1)) == 'May 1, 2011'
        assert format_date(datetime(2011, 5, 12)) == 'May 12, 2011'
        assert format_date(datetime(2011, 5, 12), format='%Y') == '2011'

    def test_format_age(self):
        assert format_age(datetime.utcnow() - timedelta(seconds = 5)) == 'just now'
        assert format_age(datetime.utcnow() - timedelta(minutes = 1)) == '1 minute ago'
        assert format_age(datetime.utcnow() - timedelta(minutes = 5)) == '5 minutes ago'
        assert format_age(datetime.utcnow() - timedelta(minutes = 60)) == '1 hour ago'
        assert format_age(datetime.utcnow() - timedelta(hours = 8)) == '8 hours ago'
        assert format_age(datetime.utcnow() - timedelta(days = 1)) == 'yesterday'
        assert format_age(datetime.utcnow() - timedelta(days = 3)) == '3 days ago'

        last_month = datetime.utcnow() - timedelta(days=28)
        assert format_age(last_month) == format_date(last_month)
