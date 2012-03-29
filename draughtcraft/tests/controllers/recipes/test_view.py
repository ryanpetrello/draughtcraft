from draughtcraft.tests     import TestAuthenticatedApp, TestApp
from draughtcraft           import model


import unittest
@unittest.expectedFailure
class TestRecipePublish(TestAuthenticatedApp):

    def test_async_get(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()
        assert self.get(
            '/recipes/1/rocky-mountain-river-ipa/async',
            status = 405
        ).status_int == 405

    def test_view_published_recipe(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User.get(1),
            state   = "PUBLISHED"
        )
        model.commit()

        response = self.get('/recipes/1/rocky-mountain-river-ipa/')
        assert response.status_int == 200

        model.Recipe.query.first().state = "DRAFT"
        model.commit()

        response = self.get('/recipes/1/rocky-mountain-river-ipa/', status=200)
        assert response.status_int == 200

    def test_invalid_primary_key(self):
        """
        If the URL contains a hex part that isn't valid hex, fail gracefully.
        /recipes/foo/<slug>
        """
        resp = self.get('/recipes/xyz/rocky-mountain-river-ipa', status=404)
        assert resp.status_int == 404

    def test_hex_lookup(self):
        """
        Make sure that the hex lookup functionality works properly with 
        hexadecimal conversion.

        e.g., the lookup for Recipe.id == 50 should be...

        /recipes/32/<slug>
        """
        model.Recipe(
            id          = 50,
            name        = 'Rocky Mountain River IPA', 
            author      = model.User.get(1),
            state       = "PUBLISHED"
        )
        model.commit()
        assert self.get('/recipes/32/rocky-mountain-river-ipa')

    def test_view_published_recipe_async(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User.get(1),
            state   = "PUBLISHED"
        )
        model.commit()

        response = self.post('/recipes/1/rocky-mountain-river-ipa/async')
        assert response.status_int == 200

        model.Recipe.query.first().state = "DRAFT"
        model.commit()

        response = self.post('/recipes/1/rocky-mountain-river-ipa/async', status=200)
        assert response.status_int == 200

        # The authenticated user is the owner, so the view count shouldn't go up.
        assert len(model.Recipe.query.first().views) == 0


@unittest.expectedFailure
class TestRecipeView(TestApp):

    def test_view_published_recipe_async(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User(first_name = 'Ryan', last_name='Petrello'),
            state   = "PUBLISHED"
        )
        model.commit()

        response = self.post('/recipes/1/rocky-mountain-river-ipa/async')
        assert response.status_int == 200

        # The visitor isn't the owner, so the view count should go up.
        assert len(model.Recipe.query.first().views) == 1

    def test_view_draft_recipe_async(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User(first_name = 'Ryan', last_name='Petrello'),
            state   = "DRAFT"
        )
        model.commit()

        response = self.get('/recipes/1/rocky-mountain-river-ipa/', status=404)
        assert response.status_int == 404
