from draughtcraft.templates.helpers     import format_percentage
from unittest                           import TestCase

class TestHelpers(TestCase):

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
