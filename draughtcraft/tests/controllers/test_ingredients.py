from draughtcraft.tests     import TestAuthenticatedApp
from draughtcraft           import model


class TestIngredientLookup(TestAuthenticatedApp):

    def test_lookup(self):
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2,
            description = 'Sample Description'
        )
        model.commit()

        assert self.get('/ingredients/1').status_int == 200
        assert self.get('/ingredients/1', status=404).status_int == 404
