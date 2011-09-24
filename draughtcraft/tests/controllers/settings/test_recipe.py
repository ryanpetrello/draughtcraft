from draughtcraft           import model
from draughtcraft.tests     import TestApp, TestAuthenticatedApp


class TestUnauthenticatedRecipeSettings(TestApp):

    def test_profile_render(self):
        assert self.get('/settings/recipe/', status=401).status_int == 401


class TestRecipeSettings(TestAuthenticatedApp):

    def test_profile_render(self):
        assert self.get('/settings/recipe/').status_int == 200

    def test_success(self):
        params = {
            'default_recipe_type'       : 'EXTRACT',
            'default_recipe_volume'     : '2.5',
            'default_ibu_formula'       : 'daniels',
            'unit_system'               : 'METRIC',
            'brewhouse_efficiency'      : 75
        }
        response = self.post('/settings/recipe/', params=params)
        assert response.status_int == 302

        user = model.User.get(1)
        assert user.settings['default_recipe_type'] == 'EXTRACT'
        assert user.settings['default_recipe_volume'] == 2.5
        assert user.settings['default_ibu_formula'] == 'daniels'
        assert user.settings['unit_system'] == 'METRIC'
        assert user.settings['brewhouse_efficiency'] == .75
