from draughtcraft.tests     import TestApp
from draughtcraft           import model

class TestRecipeBuilder(TestApp):

    def test_recipe_create(this):
        assert model.Recipe.query.count() == 0
