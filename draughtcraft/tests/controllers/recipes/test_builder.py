from draughtcraft.tests import TestApp, TestAuthenticatedApp
from draughtcraft import model


class TestAuthenticatedUserRecipeLookup(TestAuthenticatedApp):

    def test_lookup(self):
        """
        If the recipe has an author, and we're logged in as that author,
        we should have access to edit the recipe.
        """
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA'),
                model.RecipeSlug(name='American IPA (Revised)')
            ],
            author=model.User.get(1)
        )
        model.commit()

        response = self.get('/recipes/500/american-ipa/builder/', status=404)
        assert response.status_int == 404

        response = self.get('/recipes/1/american-ipa/builder/')
        assert response.status_int == 200

        response = self.get('/recipes/1/american-ipa-revised/builder/')
        assert response.status_int == 200

        response = self.get('/recipes/1/invalid_slug/builder/', status=404)
        assert response.status_int == 404

    def test_unauthorized_lookup_trial_recipe(self):
        """
        If the recipe has no author, and we're logged in as any user,
        we should *not* have access to edit the recipe.
        """
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA')
            ]
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401

    def test_unauthorized_lookup_draft(self):
        """
        If the recipe is published, and we're logged in as the author,
        we should *not* have access to edit the recipe in published form.
        """
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA')
            ],
            author=model.User.get(1),
            state='PUBLISHED'
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401

    def test_unauthorized_lookup_other_user(self):
        """
        If the recipe has an author, and we're logged in as another user,
        we should *not* have access to edit the recipe.
        """
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA')
            ],
            author=model.User()
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401


class TestTrialRecipeLookup(TestApp):

    def test_unauthorized_lookup_trial_user(self):
        """
        If the recipe has an author, and we're *not* logged in as any user,
        we should *not* have access to edit the recipe.
        """
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA')
            ],
            author=model.User.get(1)
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401

    def test_unauthorized_lookup_trial_other_user(self):
        """
        If the recipe is a trial recipe, but is not *our* trial recipe,
        we should *not* have access to edit the recipe.
        """
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA')
            ]
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401


class TestRecipePublish(TestAuthenticatedApp):

    def test_publish_get(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()

        self.get(
            '/recipes/1/rocky-mountain-river-ipa/builder/publish',
            status=405
        ).status_int == 405

    def test_simple_publish(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Fermentable(
            name='2-Row',
            origin='US',
            ppg=36,
            lovibond=2
        )
        model.commit()

        assert model.Recipe.query.first().state == "DRAFT"
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/publish')
        assert model.Recipe.query.first().state == "PUBLISHED"
