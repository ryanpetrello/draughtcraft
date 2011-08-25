from draughtcraft.tests     import TestAuthenticatedApp
from draughtcraft           import model


class TestRecipePublish(TestAuthenticatedApp):

    def test_simple_draft(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User.get(1),
            state   = "PUBLISHED"
        )
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        assert model.Recipe.query.count() == 1
        self.post('/recipes/1/rocky-mountain-river-ipa/draft')
        assert model.Recipe.query.count() == 2

        r1, r2 = model.Recipe.query.all()
        assert r1.state == "PUBLISHED"
        assert r2.state == "DRAFT"
        assert r1.current_draft == r2
        assert r2.published_version == r1

    def test_multiple_drafts(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User.get(1),
            state   = "PUBLISHED"
        )
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        assert model.Recipe.query.count() == 1
        self.post('/recipes/1/rocky-mountain-river-ipa/draft')
        assert model.Recipe.query.count() == 2

        r1, r2 = model.Recipe.query.all()
        assert r1.state == "PUBLISHED"
        assert r2.state == "DRAFT"
        assert r1.current_draft == r2
        assert r2.published_version == r1

        self.post('/recipes/1/rocky-mountain-river-ipa/draft')
        assert model.Recipe.query.count() == 2

    def test_cannot_draft_authorless_recipes(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            state   = "PUBLISHED"
        )
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        assert model.Recipe.query.count() == 1
        response = self.post('/recipes/1/rocky-mountain-river-ipa/draft', status=401)
        assert response.status_int == 401
        assert model.Recipe.query.count() == 1

    def test_cannot_draft_incorrect_author_recipes(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            state   = "PUBLISHED",
            author  = model.User()
        )
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        assert model.Recipe.query.count() == 1
        response = self.post('/recipes/1/rocky-mountain-river-ipa/draft', status=401)
        assert response.status_int == 401
        assert model.Recipe.query.count() == 1

    def test_cannot_draft_unpublished_recipes(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User.get(1)
        )
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        assert model.Recipe.query.count() == 1
        response = self.post('/recipes/1/rocky-mountain-river-ipa/draft', status=401)
        assert response.status_int == 401
        assert model.Recipe.query.count() == 1
