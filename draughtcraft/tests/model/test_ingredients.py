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
            name    = 'Cascade'
        ).printed_name == u'Cascade'

        assert model.Yeast(
            name    = 'Wyeast 1056 - American Ale'
        ).printed_name == u'Wyeast 1056 - American Ale'

    def test_excluding(self):
        model.Fermentable()
        model.Fermentable()
        model.Hop()
        model.Hop()
        model.Yeast()
        model.Yeast()
        model.commit()

        assert model.Fermentable.excluding(model.Fermentable.get(1)) == [model.Fermentable.get(2)]
        assert model.Fermentable.excluding(model.Fermentable.get(1), model.Fermentable.get(2)) == []
        assert model.Fermentable.excluding() == [model.Fermentable.get(1), model.Fermentable.get(2)]

        assert model.Hop.excluding(model.Hop.get(3)) == [model.Hop.get(4)]
        assert model.Hop.excluding(model.Hop.get(3), model.Hop.get(4)) == []
        assert model.Hop.excluding() == [model.Hop.get(3), model.Hop.get(4)]

        assert model.Yeast.excluding(model.Yeast.get(5)) == [model.Yeast.get(6)]
        assert model.Yeast.excluding(model.Yeast.get(5), model.Yeast.get(6)) == []
        assert model.Yeast.excluding() == [model.Yeast.get(5), model.Yeast.get(6)]
