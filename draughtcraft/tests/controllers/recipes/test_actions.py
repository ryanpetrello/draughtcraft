from draughtcraft.tests     import TestApp, TestAuthenticatedApp
from draughtcraft           import model


import unittest
@unittest.expectedFailure
class TestRecipeDeleteAuthenticated(TestAuthenticatedApp):

    def test_delete_get(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()
        assert self.get(
            '/recipes/1/rocky-mountain-river-ipa/delete',
            status = 405
        ).status_int == 405

    def test_recipe_delete(self):
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
        self.post('/recipes/1/rocky-mountain-river-ipa/delete')
        assert model.Recipe.query.count() == 0

    def test_cannot_delete_incorrect_author_recipes(self):
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
        response = self.post('/recipes/1/rocky-mountain-river-ipa/delete', status=401)
        assert response.status_int == 401
        assert model.Recipe.query.count() == 1


@unittest.expectedFailure
class TestRecipeDeleteUnauthenticated(TestApp):

    def test_cannot_delete_unauthenticated(self):
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
        response = self.post('/recipes/1/rocky-mountain-river-ipa/delete', status=401)
        assert response.status_int == 401
        assert model.Recipe.query.count() == 1


@unittest.expectedFailure
class TestRecipeCopyAuthenticated(TestAuthenticatedApp):

    def test_copy_get(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()
        assert self.get(
            '/recipes/1/rocky-mountain-river-ipa/copy',
            status = 405
        ).status_int == 405

    def test_recipe_copy(self):
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
        self.post('/recipes/1/rocky-mountain-river-ipa/copy')
        assert model.Recipe.query.count() == 2

        for r in model.Recipe.query.all():
            assert r.author == model.User.query.first()
            assert r.copied_from == None

        assert model.Recipe.get_by(name = 'Rocky Mountain River IPA (Duplicate)') is not None

    def test_copy_other_users_recipe(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User(),
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
        self.post('/recipes/1/rocky-mountain-river-ipa/copy')
        assert model.Recipe.query.count() == 2

        for r in model.Recipe.query.all():
            assert r.name == 'Rocky Mountain River IPA'

        recipes = model.Recipe.query.order_by('id').all()
        assert recipes[0].author
        assert recipes[1].author
        assert recipes[0].author != recipes[1].author
        assert recipes[0].copies == [recipes[1]]
        assert recipes[1].copied_from == recipes[0]

    def test_recipe_copy_anonymous_recipe(self):
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
        resp = self.post('/recipes/1/rocky-mountain-river-ipa/copy', status=401)
        assert resp.status_int == 401
        assert model.Recipe.query.count() == 1


@unittest.expectedFailure
class TestRecipeCopyUnauthenticated(TestApp):

    def test_cannot_copy_recipe_as_visitor(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User(),
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
        response = self.post('/recipes/1/rocky-mountain-river-ipa/copy', status=302)
        assert response.status_int == 302
        assert response.headers['Location'].endswith('/signup')
        assert model.Recipe.query.count() == 1


@unittest.expectedFailure
class TestRecipePublish(TestAuthenticatedApp):

    def test_draft_get(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()
        assert self.get(
            '/recipes/1/rocky-mountain-river-ipa/draft',
            status = 405
        ).status_int == 405

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

        r1, r2 = model.Recipe.query.order_by(model.Recipe.id).all()
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

        r1, r2 = model.Recipe.query.order_by(model.Recipe.id).all()
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
