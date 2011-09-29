from draughtcraft.tests     import TestAuthenticatedApp
from draughtcraft           import model


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

        response = self.get('/recipes/1/rocky-mountain-river-ipa/', status=404)
        assert response.status_int == 404

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

        response = self.post('/recipes/1/rocky-mountain-river-ipa/async', status=404)
        assert response.status_int == 404

        assert len(model.Recipe.query.first().views) == 1
