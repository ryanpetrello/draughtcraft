from draughtcraft.tests     import TestApp
from draughtcraft           import model


class TestRecipeLookup(TestApp):

    def test_lookup(self):
        model.Recipe(
            name    = 'American IPA',
            slugs   = [
                model.RecipeSlug('American IPA'),
                model.RecipeSlug('American IPA (Revised)')
            ]
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
