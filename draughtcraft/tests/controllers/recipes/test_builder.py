from json import dumps
from datetime import timedelta

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

        response = self.get('/recipes/500/american-ipa/builder', status=404)
        assert response.status_int == 404

        response = self.get('/recipes/1/american-ipa/builder')
        assert response.status_int == 200

        response = self.get('/recipes/1/american-ipa-revised/builder')
        assert response.status_int == 200

        response = self.get('/recipes/1/invalid_slug/builder', status=404)
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

        response = self.get('/recipes/1/american-ipa/builder', status=401)
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

        response = self.get('/recipes/1/american-ipa/builder', status=401)
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

        response = self.get('/recipes/1/american-ipa/builder', status=401)
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

        response = self.get('/recipes/1/american-ipa/builder', status=401)
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

        response = self.get('/recipes/1/american-ipa/builder', status=401)
        assert response.status_int == 401


class TestRecipeSave(TestAuthenticatedApp):

            #u'mash': {
            #    u'additions': [{
            #        u'amount': 5,
            #        u'minutes': 60,
            #        u'use': u'MASH',
            #        u'unit': u'POUND',
            #        u'ingredient': {
            #            u'ppg': 36,
            #            u'name': u'Pilsner Malt (Belgian)',
            #            u'lovibond': 1.6,
            #            u'printed_type':
            #            u'Grain',
            #            u'class': u'Fermentable',
            #            u'id': 354
            #        }
            #    }]
            #},
            #u'boil': {
            #    u'additions': [{
            #        u'use': u'BOIL',
            #        u'form': u'PELLET',
            #        u'alpha_acid': 4.5,
            #        u'amount': 0.75,
            #        u'minutes': 60,
            #        u'unit': u'OUNCE',
            #        u'ingredient': {
            #            u'class': u'Hop',
            #            u'id': 440,
            #            u'alpha_acid': 4.5,
            #            u'name': u'Cascade (US)'
            #        }
            #    }]
            #},
            #u'fermentation': {
            #    u'additions': [{
            #        u'amount': 1,
            #        u'minutes': 60,
            #        u'use': u'PRIMARY',
            #        u'unit': u'POUND',
            #        u'ingredient': {
            #            u'class': u'Yeast',
            #            u'attenuation': 0.74,
            #            u'id': 545,
            #            u'form': u'Liquid',
            #            u'name': u'Wyeast 3944 - Belgian Witbier'
            #        }
            #    }]
            #}

    def test_name_update(self):
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA'),
                model.RecipeSlug(name='American IPA (Revised)')
            ],
            author=model.User.get(1)
        )
        model.commit()

        response = self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={
                'recipe': dumps({'name': 'Some Recipe'})
            }
        )
        assert response.status_int == 200
        recipe = model.Recipe.query.first()
        assert recipe.name == 'Some Recipe'

        slugs = recipe.slugs
        assert len(slugs) == 3
        assert slugs[0].slug == 'american-ipa'
        assert slugs[1].slug == 'american-ipa-revised'
        assert slugs[2].slug == 'some-recipe'

    def test_volume_update(self):
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA'),
                model.RecipeSlug(name='American IPA (Revised)')
            ],
            author=model.User.get(1)
        )
        model.commit()

        response = self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={
                'recipe': dumps({'volume': 10})
            }
        )
        assert response.status_int == 200
        recipe = model.Recipe.query.first()
        assert recipe.gallons == 10

    def test_style_save(self):
        model.Style(name='Some Style')
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA'),
                model.RecipeSlug(name='American IPA (Revised)')
            ],
            author=model.User.get(1)
        )
        model.commit()

        response = self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={
                'recipe': dumps({'style': 1})
            }
        )
        assert response.status_int == 200
        recipe = model.Recipe.query.first()
        assert recipe.style.name == 'Some Style'

    def test_style_remove(self):
        model.Recipe(
            name='American IPA',
            slugs=[
                model.RecipeSlug(name='American IPA'),
                model.RecipeSlug(name='American IPA (Revised)')
            ],
            style=model.Style(name='Some Style'),
            author=model.User.get(1)
        )
        model.commit()

        response = self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={
                'recipe': dumps({'style': None})
            }
        )
        assert response.status_int == 200
        recipe = model.Recipe.query.first()
        assert recipe.style is None


class TestMashAdditions(TestAuthenticatedApp):

    def test_fermentable(self):
        model.Recipe(
            name='American IPA',
            author=model.User.get(1)
        )
        model.Fermentable(
            name='2-Row',
            origin='US',
            ppg=36,
            lovibond=2
        )
        model.commit()

        data = {
            u'mash': {
                u'additions': [{
                    u'amount': 5,
                    u'unit': u'POUND',
                    u'ingredient': {
                        u'id': 1,
                        u'class': 'Fermentable'
                    }
                }]
            }
        }

        self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={'recipe': dumps(data)}
        )

        assert model.RecipeAddition.query.count() == 1
        a = model.RecipeAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.amount == 5
        assert a.unit == 'POUND'
        assert a.fermentable == model.Fermentable.get(1)

    def test_hop(self):
        model.Recipe(
            name='American IPA',
            author=model.User.get(1)
        )
        model.Hop(name='Cascade', origin='US')
        model.commit()

        data = {
            u'mash': {
                u'additions': [{
                    u'use': u'MASH',
                    u'form': u'PELLET',
                    u'alpha_acid': 8,
                    u'amount': 16,
                    u'duration': 60,
                    u'unit': u'OUNCE',
                    u'ingredient': {
                        u'id': 1,
                        u'class': u'Hop'
                    }
                }]
            }
        }

        self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={'recipe': dumps(data)}
        )

        assert model.HopAddition.query.count() == 1
        a = model.HopAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.amount == 16
        assert a.duration == timedelta(minutes=60)
        assert a.unit == 'OUNCE'
        assert a.form == 'PELLET'
        assert a.alpha_acid == 8
        assert a.hop == model.Hop.get(1)


class TestHopAdditions(TestAuthenticatedApp):

    def test_fermentable(self):
        model.Recipe(
            name='American IPA',
            author=model.User.get(1)
        )
        model.Fermentable(
            name='2-Row',
            origin='US',
            ppg=36,
            lovibond=2
        )
        model.commit()

        data = {
            u'boil': {
                u'additions': [{
                    u'amount': 5,
                    u'use': 'BOIL',
                    u'duration': 15,
                    u'unit': u'POUND',
                    u'ingredient': {
                        u'id': 1,
                        u'class': 'Fermentable'
                    }
                }]
            }
        }

        self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={'recipe': dumps(data)}
        )

        assert model.RecipeAddition.query.count() == 1
        a = model.RecipeAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.amount == 5
        assert a.use == 'BOIL'
        assert a.duration == timedelta(minutes=15)
        assert a.unit == 'POUND'
        assert a.fermentable == model.Fermentable.get(1)

    def test_hop(self):
        model.Recipe(
            name='American IPA',
            author=model.User.get(1)
        )
        model.Hop(name='Cascade', origin='US')
        model.commit()

        data = {
            u'boil': {
                u'additions': [{
                    u'use': u'BOIL',
                    u'form': u'PELLET',
                    u'alpha_acid': 8,
                    u'amount': 16,
                    u'duration': 60,
                    u'unit': u'OUNCE',
                    u'ingredient': {
                        u'id': 1,
                        u'class': u'Hop'
                    }
                }]
            }
        }

        self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={'recipe': dumps(data)}
        )

        assert model.HopAddition.query.count() == 1
        a = model.HopAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.amount == 16
        assert a.use == 'BOIL'
        assert a.duration == timedelta(minutes=60)
        assert a.unit == 'OUNCE'
        assert a.form == 'PELLET'
        assert a.alpha_acid == 8
        assert a.hop == model.Hop.get(1)


class TestFermentationAdditions(TestAuthenticatedApp):

    def test_hop(self):
        model.Recipe(
            name='American IPA',
            author=model.User.get(1)
        )
        model.Hop(name='Cascade', origin='US')
        model.commit()

        data = {
            u'fermentation': {
                u'additions': [{
                    u'use': u'SECONDARY',
                    u'form': u'PELLET',
                    u'alpha_acid': 8,
                    u'amount': 16,
                    u'unit': u'OUNCE',
                    u'ingredient': {
                        u'id': 1,
                        u'class': u'Hop'
                    }
                }]
            }
        }

        self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={'recipe': dumps(data)}
        )

        assert model.HopAddition.query.count() == 1
        a = model.HopAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.amount == 16
        assert a.use == 'SECONDARY'
        assert a.unit == 'OUNCE'
        assert a.form == 'PELLET'
        assert a.alpha_acid == 8
        assert a.hop == model.Hop.get(1)

    def test_yeast(self):
        model.Recipe(
            name='American IPA',
            author=model.User.get(1)
        )
        model.Yeast(
            name='Wyeast 1056 - American Ale',
            form='LIQUID',
            attenuation=.75
        )
        model.commit()

        data = {
            u'mash': {
                u'additions': [{
                    u'use': u'MASH',
                    u'amount': 1,
                    u'use': 'PRIMARY',
                    u'ingredient': {
                        u'id': 1,
                        u'class': u'Yeast'
                    }
                }]
            }
        }

        self.post(
            '/recipes/1/american-ipa/builder?_method=PUT',
            params={'recipe': dumps(data)}
        )

        assert model.RecipeAddition.query.count() == 1
        a = model.RecipeAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.amount == 1
        assert a.use == 'PRIMARY'
        assert a.yeast == model.Yeast.get(1)


class TestRecipePublish(TestAuthenticatedApp):

    def test_publish_get(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()

        self.get(
            '/recipes/1/rocky-mountain-river-ipa/builder/publish',
            status=404
        ).status_int == 404

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
