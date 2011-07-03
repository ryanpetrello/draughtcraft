from draughtcraft.tests     import TestApp, TestAuthenticatedApp
from draughtcraft           import model


class TestRecipeCreation(TestApp):

    def test_creation(self):
        assert model.Recipe.query.count() == 0
        self.get('/recipes/create')
        assert model.Recipe.query.count() == 0

    def test_schema_validation(self):
        params = {
            'name'      : 'Rocky Mountain River IPA',
            'type'      : 'MASH',
            'volume'    : 5,
            'unit'      : 'GALLON'
        }
        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/recipes/create', params=copy)
            assert response.status_int == 200
            assert 'validation_errors' in response.request.pecan

        assert model.Recipe.query.count() == 0

    def test_success(self):
        params = {
            'name'      : 'Rocky Mountain River IPA',
            'type'      : 'MASH',
            'volume'    : 25,
            'unit'      : 'GALLON'
        }

        response = self.post('/recipes/create', params=params)

        assert model.Recipe.query.count() == 1
        r = model.Recipe.get(1)
        assert r.type == 'MASH'
        assert r.name == u'Rocky Mountain River IPA'
        assert r.gallons == 25
        assert len(r.slugs) == 1
        assert r.slugs[0].slug == 'rocky-mountain-river-ipa'

        assert len(r.fermentation_steps) == 1
        assert r.fermentation_steps[0].step == 'PRIMARY'

        assert response.status_int == 302
        assert response.headers['Location'].endswith('/recipes/1/rocky-mountain-river-ipa/builder')


class TestUserRecipeCreation(TestAuthenticatedApp):

    def test_recipe_author(self):
        params = {
            'name'      : 'Rocky Mountain River IPA',
            'type'      : 'MASH',
            'volume'    : 25,
            'unit'      : 'GALLON'
        }

        self.post('/recipes/create', params=params)

        assert model.Recipe.query.count() == 1
        r = model.Recipe.get(1)
        assert r.author.id == 1