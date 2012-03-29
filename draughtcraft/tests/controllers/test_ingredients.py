from draughtcraft.tests     import TestApp, TestAuthenticatedApp
from draughtcraft           import model


import unittest
@unittest.expectedFailure
class TestUnauthenticatedIngredientLookup(TestApp):

    def test_lookup(self):
        model.Fermentable(
            name        = '2-Row',
            type        = 'MALT',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2,
            description = 'Sample Description'
        )
        model.commit()

        assert self.get('/ingredients/1').status_int == 200
        assert self.get('/ingredients/2', status=404).status_int == 404


@unittest.expectedFailure
class TestAuthenticatedIngredientLookup(TestAuthenticatedApp):

    def test_lookup(self):
        model.Fermentable(
            name        = '2-Row',
            type        = 'MALT',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2,
            description = 'Sample Description'
        )
        model.commit()

        assert self.get('/ingredients/1').status_int == 200
        assert self.get('/ingredients/2', status=404).status_int == 404
