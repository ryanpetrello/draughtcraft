from draughtcraft       import model
from draughtcraft.tests import TestApp


class TestIngredients(TestApp):

    def test_printed_name(self): 
        assert model.Fermentable(
            name    = '2-Row',
            origin  = 'US'
        ).printed_name == u'2-Row (US)'

        assert model.Fermentable(
            name    = '2-Row',
            origin  = 'BELGIAN'
        ).printed_name == u'2-Row (Belgian)'

        assert model.Hop(
            name    = 'Cascade',
            origin  = 'US'
        ).printed_name == u'Cascade (US)'

        assert model.Hop(
            name    = 'Cascade',
            origin  = 'BELGIAN'
        ).printed_name == u'Cascade (Belgian)'

        assert model.Yeast(
            name    = 'Wyeast 1056 - American Ale'
        ).printed_name == u'Wyeast 1056 - American Ale'

    def test_printed_type(self):
        assert model.Fermentable().printed_type == 'Grain'
        assert model.Fermentable(type='SUGAR').printed_type == 'Sugar'
        assert model.Fermentable(type='MALT').printed_type == 'Grain'
