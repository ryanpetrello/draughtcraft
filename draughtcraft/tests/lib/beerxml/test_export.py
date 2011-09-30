from draughtcraft.lib.beerxml       import export
from unittest                       import TestCase


class TestExport(TestCase):

    def prepare_xml(self, xml):
        return ''.join([n.strip() for n in xml])


class TestHop(TestExport):

    def test_hop_export(self):
        assert export.Hop(
            name    = 'Target',
            alpha   = 10.5,
            amount  = 0.0625,
            use     = 'BOIL',
            time    = 60,
            notes   = 'English mid-to-high alpha hop bred from Kent Goldings.',
            form    = 'LEAF',
            origin  = 'GERMAN'
        ).render() == self.prepare_xml([
            '<HOP>',
            '   <ALPHA>10.5</ALPHA>',
            '   <AMOUNT>0.0625</AMOUNT>',
            '   <FORM>LEAF</FORM>',
            '   <NAME>Target</NAME>',
            '   <NOTES>English mid-to-high alpha hop bred from Kent Goldings.</NOTES>',
            '   <ORIGIN>GERMAN</ORIGIN>',
            '   <TIME>60</TIME>',
            '   <USE>BOIL</USE>',
            '   <VERSION>1</VERSION>',
            '</HOP>'
        ])
