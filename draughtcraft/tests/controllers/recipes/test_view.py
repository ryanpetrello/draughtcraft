from draughtcraft.tests     import TestAuthenticatedApp
from draughtcraft           import model


class TestRecipePublish(TestAuthenticatedApp):

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

    def test_view_published_recipe_async(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User.get(1),
            state   = "PUBLISHED"
        )
        model.commit()

        response = self.get('/recipes/1/rocky-mountain-river-ipa/async')
        assert response.status_int == 200

        model.Recipe.query.first().state = "DRAFT"
        model.commit()

        response = self.get('/recipes/1/rocky-mountain-river-ipa/async', status=404)
        assert response.status_int == 404
