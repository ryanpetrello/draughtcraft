from draughtcraft.tests     import TestApp
from draughtcraft           import model

class TestRecipeBuilder(TestApp):

    def test_recipe_create(self):
        assert model.Recipe.query.count() == 0

        response = self.get('/recipes/create')
        assert response.status_int == 302

        assert model.Recipe.query.count() == 1
        assert response.headers['Location'].endswith('/recipes/1/builder')
