from draughtcraft.tests     import TestApp
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
            'gallons'   : 5
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
            'gallons'   : 5
        }

        response = self.post('/recipes/create', params=params)
        assert response.status_int == 302
        assert response.headers['Location'].endswith('/recipes/1/american-ale/builder')
        assert model.Recipe.query.count() == 1
        r = model.Recipe.get(1)
        assert r.name == u'Rocky Mountain River IPA'
