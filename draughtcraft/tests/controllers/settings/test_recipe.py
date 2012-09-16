from draughtcraft import model
from draughtcraft.tests import TestApp, TestAuthenticatedApp


class TestUnauthenticatedRecipeSettings(TestApp):

    def test_profile_render(self):
        resp = self.get('/settings/recipe/', status=302)
        assert resp.status_int == 302
        assert resp.headers['Location'].endswith('/signup')


class TestRecipeSettings(TestAuthenticatedApp):

    def test_profile_render(self):
        assert self.get('/settings/recipe/').status_int == 200

    def test_success(self):
        params = {
            'default_recipe_type': 'EXTRACT',
            'default_recipe_volume': '2.5',
            'default_ibu_formula': 'daniels',
            'unit_system': 'METRIC',
            'brewhouse_efficiency': 75
        }
        response = self.post('/settings/recipe/', params=params)
        assert response.status_int == 302

        user = model.User.get(1)
        assert user.settings['default_recipe_type'] == 'EXTRACT'
        assert user.settings['default_recipe_volume'] == 2.5
        assert user.settings['default_ibu_formula'] == 'daniels'
        assert user.settings['unit_system'] == 'METRIC'
        assert user.settings['brewhouse_efficiency'] == .75

    def test_metric_volume_default(self):
        user = model.User.get(1)
        user.settings['unit_system'] = 'METRIC'
        model.commit()

        params = {
            'default_recipe_type': 'EXTRACT',
            'default_recipe_volume': '10',  # (in liters)
            'default_ibu_formula': 'daniels',
            'unit_system': 'METRIC',
            'brewhouse_efficiency': 75
        }
        response = self.post('/settings/recipe/', params=params)
        assert response.status_int == 302

        user = model.User.get(1)
        assert user.settings['default_recipe_type'] == 'EXTRACT'
        assert user.settings['default_recipe_volume'] == 2.64172052
        assert user.settings['default_ibu_formula'] == 'daniels'
        assert user.settings['unit_system'] == 'METRIC'
        assert user.settings['brewhouse_efficiency'] == .75


class TestAnonymousVisitorSettings(TestApp):

    def test_unit_get(self):
        assert self.get('/units', status=405).status_int == 405

    def test_unit_system_toggle(self):
        resp = self.get('/')
        session = resp.request.environ['beaker.session']
        assert 'metric' not in session

        # Toggle to metric
        self.post('/units')

        resp = self.get('/')
        session = resp.request.environ['beaker.session']
        assert session['metric'] is True

        # Toggle to US
        self.post('/units')

        resp = self.get('/')
        session = resp.request.environ['beaker.session']
        assert session['metric'] is False

        # Toggle back to metric
        self.post('/units')

        resp = self.get('/')
        session = resp.request.environ['beaker.session']
        assert session['metric'] is True
