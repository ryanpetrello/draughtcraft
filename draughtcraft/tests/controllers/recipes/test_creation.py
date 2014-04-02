from draughtcraft.tests import TestApp, TestAuthenticatedApp
from draughtcraft import model


class TestRecipeCreation(TestApp):

    def test_creation(self):
        assert model.Recipe.query.count() == 0
        self.get('/recipes/create')
        assert model.Recipe.query.count() == 0

    def test_only_one_trial_recipe_allowed(self):
        """
        If you're not authenticated, and you create a recipe, and then attempt
        to make another, you should be automatically redirected to your first
        recipe.
        """
        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 25,
            'unit': 'GALLON'
        }

        self.post('/recipes/create', params=params)

        response = self.get('/recipes/create')
        assert response.status_int == 302
        assert response.headers['Location'].endswith(
            '/recipes/1/rocky-mountain-river-ipa/builder'
        )

    def test_schema_validation(self):
        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 5,
            'unit': 'GALLON'
        }
        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/recipes/create', params=copy)
            assert response.status_int == 200
            assert len(self.get_form(response).errors)

        assert model.Recipe.query.count() == 0

    def test_success(self):
        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 25,
            'unit': 'GALLON'
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
        assert response.headers['Location'].endswith(
            '/recipes/1/rocky-mountain-river-ipa/builder')

        #
        # Because the user isn't logged in, we'll assume they're a guest
        # and store the recipe as a `trial_recipe` in their session.
        #
        assert 'trial_recipe_id' in response.request.environ['beaker.session']

        #
        # Make sure we're allowed to view/edit the new recipe.
        #
        assert response.follow().status_int == 200


class TestUserRecipeCreation(TestAuthenticatedApp):

    def test_recipe_author(self):
        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 25,
            'unit': 'GALLON'
        }

        self.post('/recipes/create', params=params)

        assert model.Recipe.query.count() == 1
        r = model.Recipe.get(1)
        assert r.author.id == 1

    def test_metric_recipe(self):
        user = model.User.get(1)
        user.settings['unit_system'] = 'METRIC'
        model.commit()

        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 10,
            'unit': 'LITER'
        }

        self.post('/recipes/create', params=params)

        assert model.Recipe.query.count() == 1
        r = model.Recipe.get(1)
        assert r.gallons == 2.64172052

    def test_recipe_author_no_trial_recipe(self):
        """
        If the recipe is created by an authenticated user, a `trial_recipe_id`
        should not be stored in the session.
        """
        params = {
            'name': 'Rocky Mountain River IPA',
            'type': 'MASH',
            'volume': 25,
            'unit': 'GALLON'
        }

        response = self.post('/recipes/create', params=params)

        assert model.Recipe.query.count() == 1
        r = model.Recipe.get(1)
        assert r.author.id == 1

        assert 'trial_recipe_id' not in response.request.environ[
            'beaker.session']

    def test_default_settings_for_first_recipe(self):
        """
        If the created recipe is the first recipe for the authenticated user,
        store their chosen settings as defaults (they're likely to use them
        again next time).
        """
        params = {
            'name': 'Rocky Mountain River IPA (Extract)',
            'type': 'EXTRACT',
            'volume': 25,
            'unit': 'GALLON'
        }
        self.post('/recipes/create', params=params)

        r = model.Recipe.get(1)
        assert r.author.settings['default_recipe_type'] == 'EXTRACT'
        assert r.author.settings['default_recipe_volume'] == 25

        # This is not the first recipe, so we shouldn't save new defaults.
        params = {
            'name': 'Rocky Mountain River IPA (All-Grain)',
            'type': 'MASH',
            'volume': 5,
            'unit': 'GALLON'
        }
        self.post('/recipes/create', params=params)

        r = model.Recipe.get(2)
        assert r.author.settings['default_recipe_type'] == 'EXTRACT'
        assert r.author.settings['default_recipe_volume'] == 25
