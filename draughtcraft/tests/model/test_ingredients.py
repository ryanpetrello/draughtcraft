from draughtcraft       import model


class TestIngredients(object):

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
            name    = 'Cascade'
        ).printed_name == u'Cascade'

        assert model.Yeast(
            name    = 'Wyeast 1056 - American Ale'
        ).printed_name == u'Wyeast 1056 - American Ale'
