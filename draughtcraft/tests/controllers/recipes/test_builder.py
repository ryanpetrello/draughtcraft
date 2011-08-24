from draughtcraft.tests     import TestApp, TestAuthenticatedApp
from draughtcraft           import model
from datetime               import timedelta


class TestMashAdditions(TestAuthenticatedApp):

    def test_fermentable(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'type'          : 'RecipeAddition',
            'ingredient'    : 1,
            'use'           : 'MASH',
            'amount'        : '0 lb'
        })

        assert model.RecipeAddition.query.count() == 1
        a = model.RecipeAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.use == 'MASH'
        assert a.amount == 0
        assert a.unit == 'POUND'
        assert a.fermentable == model.Fermentable.get(1)

    def test_hop(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Hop(name = 'Cascade', origin = 'US')
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'type'          : 'HopAddition',
            'ingredient'    : 1,
            'use'           : 'MASH',
            'amount'        : '0 lb'
        })

        assert model.HopAddition.query.count() == 1
        a = model.HopAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.use == 'MASH'
        assert a.amount == 0
        assert a.unit == 'POUND'
        assert a.hop == model.Hop.get(1)

    def test_schema_failure(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Fermentable(name = '2-Row', origin='US')
        model.commit()
       
        params = {
            'type'          : 'RecipeAddition',
            'ingredient'    : 1,
            'use'           : 'MASH',
            'amount'        : '0 lb'
        }        

        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestBoilAdditions(TestAuthenticatedApp):

    def test_fermentable(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'type'          : 'RecipeAddition',
            'ingredient'    : 1,
            'use'           : 'BOIL',
            'amount'        : '0 lb'
        })

        assert model.RecipeAddition.query.count() == 1
        a = model.RecipeAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.use == 'BOIL'
        assert a.amount == 0
        assert a.unit == 'POUND'
        assert a.fermentable == model.Fermentable.get(1)

    def test_hop(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5,
            origin      = 'US'
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'type'          : 'HopAddition',
            'ingredient'    : 1,
            'use'           : 'BOIL',
            'amount'        : '0 lb',
            'duration'      : 30
        })

        assert model.HopAddition.query.count() == 1
        a = model.HopAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.use == 'BOIL'
        assert a.amount == 0
        assert a.unit == 'POUND'
        assert a.hop == model.Hop.get(1)
        assert a.minutes == 30
        assert a.alpha_acid == 5.5

    def test_schema_failure(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Fermentable(name = '2-Row', origin='US')
        model.commit()
       
        params = {
            'type'          : 'RecipeAddition',
            'ingredient'    : 1,
            'use'           : 'BOIL',
            'amount'        : '0 lb'
        }        

        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestFermentationAdditions(TestAuthenticatedApp):

    def test_hop(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5,
            origin      = 'US'
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'type'          : 'HopAddition',
            'ingredient'    : 1,
            'use'           : 'SECONDARY',
            'amount'        : '0 lb'
        })

        assert model.HopAddition.query.count() == 1
        a = model.HopAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.use == 'SECONDARY'
        assert a.amount == 0
        assert a.unit == 'POUND'
        assert a.hop == model.Hop.get(1)
        assert a.alpha_acid == 5.5

    def test_yeast(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Yeast(
            name = 'Wyeast 1056 - American Ale',
            form = 'LIQUID',
            attenuation = .75
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'type'          : 'RecipeAddition',
            'ingredient'    : 1,
            'use'           : 'PRIMARY',
            'amount'        : '1'
        })

        assert model.RecipeAddition.query.count() == 1
        a = model.RecipeAddition.get(1)
        assert a.recipe == model.Recipe.get(1)
        assert a.use == 'PRIMARY'
        assert a.yeast == model.Yeast.get(1)

    def test_schema_failure(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5
        )
        model.commit()
       
        params = {
            'type'          : 'HopAddition',
            'ingredient'    : 1,
            'use'           : 'PRIMARY',
            'amount'        : '0 lb'
        }        

        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestRecipeSettings(TestAuthenticatedApp):

    def test_style_change(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.Style(name = u'American Ale')
        model.commit()

        assert model.Recipe.get(1).style is None
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/style', params={
            'target': 1
        })
        
        assert model.Recipe.get(1).style == model.Style.get(1)

    def test_style_remove(self):
        recipe = model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        recipe.style = model.Style(name = u'American Ale')
        model.commit()

        assert model.Recipe.get(1).style == model.Style.get(1)
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/style', params={
            'target': '' 
        })
        
        assert model.Recipe.get(1).style is None

    def test_boil_duration_change(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()

        assert model.Recipe.get(1).boil_minutes == 60
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/boil_minutes', params={
            'minutes'    : 90
        })
        
        assert model.Recipe.get(1).boil_minutes == 90

    def test_volume_change(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()

        assert model.Recipe.get(1).gallons == 5.0
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/volume', params={
            'volume'    : 10.0,
            'unit'      : 'GALLON' 
        })
        
        assert model.Recipe.get(1).gallons == 10.0

    def test_notes_update(self):
        model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        model.commit()

        assert model.Recipe.get(1).notes is None
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/notes', params={
            'notes'    : u'Testing 1 2 3...'
        })
        
        assert model.Recipe.get(1).notes == u'Testing 1 2 3...'


class TestFermentationStepChange(TestAuthenticatedApp):

    def test_fermentation_step_add(self):
        recipe = model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        recipe.fermentation_steps.append(
            model.FermentationStep(
                step = 'PRIMARY',
                days = 7,
                fahrenheit = 65
            )
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/fermentation_steps')

        recipe = model.Recipe.get(1)
        assert len(recipe.fermentation_steps) == 2
        assert recipe.fermentation_steps[0].step == 'PRIMARY'
        assert recipe.fermentation_steps[0].days == 7
        assert recipe.fermentation_steps[0].fahrenheit == 65
        assert recipe.fermentation_steps[1].step == 'SECONDARY'
        assert recipe.fermentation_steps[1].days == 7
        assert recipe.fermentation_steps[1].fahrenheit == 65

    def test_fermentation_step_update(self):
        recipe = model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        recipe.fermentation_steps.append(
            model.FermentationStep(
                step = 'PRIMARY',
                days = 7,
                fahrenheit = 65
            )
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/fermentation_steps?_method=put', params={
            'step'          : 1,
            'days'          : 14,
            'temperature'   : 68
        })

        recipe = model.Recipe.get(1)
        assert model.FermentationStep.query.count() == 1
        assert len(recipe.fermentation_steps) == 1
        assert recipe.fermentation_steps[0].step == 'PRIMARY'
        assert recipe.fermentation_steps[0].days == 14
        assert recipe.fermentation_steps[0].fahrenheit == 68

    def test_fermentation_step_delete(self):
        recipe = model.Recipe(name='Rocky Mountain River IPA', author=model.User.get(1))
        recipe.fermentation_steps.extend([
            model.FermentationStep(
                step = 'PRIMARY',
                days = 7,
                fahrenheit = 65
            ),
            model.FermentationStep(
                step = 'SECONDARY',
                days = 14,
                fahrenheit = 50
            )
        ])
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/fermentation_steps?_method=delete')

        recipe = model.Recipe.get(1)
        assert len(recipe.fermentation_steps) == 1
        assert recipe.fermentation_steps[0].step == 'PRIMARY'
        assert recipe.fermentation_steps[0].days == 7
        assert recipe.fermentation_steps[0].fahrenheit == 65


class TestRecipeChange(TestAuthenticatedApp):

    def test_mash_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            fermentable = model.Fermentable(
                name        = '2-Row',
                origin      = 'US',
                ppg         = 36,
                lovibond    = 2
            ),
            amount      = 12,
            unit        = 'POUND',
            use         = 'MASH'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'mash_additions-0.type'          : 'RecipeAddition',
            'mash_additions-0.amount'        : '10 lb',
            'mash_additions-0.use'           : 'MASH',
            'mash_additions-0.addition'      : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'MASH'
        assert a.amount == 10
        assert a.unit == 'POUND'
        assert a.ingredient == model.Fermentable.get(1)

    def test_unitless_mash_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            fermentable = model.Fermentable(
                name            = '2-Row',
                origin          = 'US',
                ppg             = 36,
                lovibond        = 2,
                default_unit    = 'POUND'
            ),
            amount      = 12,
            unit        = 'GALLON', # This doesn't make sense, but it's just 
                                    # for illustration
            use         = 'MASH'
        )
        model.commit()

        #
        # If an amount is specified without a unit,
        # the unit should fall back to the ingredient's
        # default unit.
        #
        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'mash_additions-0.type'          : 'RecipeAddition',
            'mash_additions-0.amount'        : '5',
            'mash_additions-0.use'           : 'MASH',
            'mash_additions-0.addition'      : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'MASH'
        assert a.amount == 5
        assert a.unit == 'POUND'
        assert a.ingredient == model.Fermentable.get(1)

    def test_boil_hop_change(self):
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            author      = model.User.get(1)
        )
        model.HopAddition(
            recipe      = recipe,
            hop         = model.Hop(name = 'Cascade', origin = 'US'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.HopAddition(
            recipe      = recipe,
            hop         = model.Hop(name = 'Centennial', origin = 'US'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=60),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'boil_additions-0.type'          : 'HopAddition',
            'boil_additions-0.amount'        : '2 oz',
            'boil_additions-0.use'           : 'BOIL',
            'boil_additions-0.alpha_acid'    : 7,
            'boil_additions-0.duration'      : 10,
            'boil_additions-0.addition'      : 1,
            'boil_additions-0.form'          : 'PELLET',
            'boil_additions-1.type'          : 'HopAddition',
            'boil_additions-1.amount'        : '.5 oz',
            'boil_additions-1.use'           : 'BOIL',
            'boil_additions-1.alpha_acid'    : 4,
            'boil_additions-1.duration'      : 45,
            'boil_additions-1.addition'      : 2,
            'boil_additions-1.form'          : 'PLUG'
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'BOIL'
        assert a.amount == .125
        assert a.unit == 'POUND'
        assert a.ingredient == model.Hop.get(1)
        assert a.alpha_acid == 7
        assert a.duration == timedelta(minutes=10)
        assert a.form == 'PELLET'

        a = model.RecipeAddition.get(2)
        assert a.use == 'BOIL'
        assert a.amount == .03125
        assert a.unit == 'POUND'
        assert a.ingredient == model.Hop.get(2)
        assert a.alpha_acid == 4
        assert a.duration == timedelta(minutes=45)
        assert a.form == 'PLUG'

    def test_boil_hop_change_first_wort(self):
        """
        If hops are added a "FIRST WORT",
        then the duration (for calculation purposes)
        should forcibly be set to the recipe-specified
        boil duration (by default, this is 60 minutes).
        """
        model.HopAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            hop         = model.Hop(name = 'Cascade', origin = 'US'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'boil_additions-0.type'          : 'HopAddition',
            'boil_additions-0.amount'        : '2 oz',
            'boil_additions-0.use'           : 'FIRST WORT',
            'boil_additions-0.alpha_acid'    : 7,
            'boil_additions-0.duration'      : 30,
            'boil_additions-0.addition'      : 1,
            'boil_additions-0.form'          : 'PELLET'
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'FIRST WORT'
        assert a.amount == .125
        assert a.unit == 'POUND'
        assert a.ingredient == model.Hop.get(1)
        assert a.alpha_acid == 7
        assert a.duration == timedelta(minutes=60)
        assert a.form == 'PELLET'

    def test_boil_hop_change_flame_out(self):
        """
        If hops are added a "FLAME OUT",
        then the duration (for calculation purposes)
        should forcibly be set zero minutes. 
        """
        model.HopAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            hop         = model.Hop(name = 'Cascade', origin = 'US'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'boil_additions-0.type'          : 'HopAddition',
            'boil_additions-0.amount'        : '2 oz',
            'boil_additions-0.use'           : 'FLAME OUT',
            'boil_additions-0.alpha_acid'    : 7,
            'boil_additions-0.duration'      : 30,
            'boil_additions-0.addition'      : 1,
            'boil_additions-0.form'          : 'PELLET'
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'FLAME OUT'
        assert a.amount == .125
        assert a.unit == 'POUND'
        assert a.ingredient == model.Hop.get(1)
        assert a.alpha_acid == 7
        assert a.duration == timedelta(minutes=0)
        assert a.form == 'PELLET'

    def test_yeast_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            yeast       = model.Yeast(
                name = 'Wyeast 1056 - American Ale',
                form = 'LIQUID',
                attenuation = .75
            ),
            amount      = 1,
            use         = 'PRIMARY'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params={
            'fermentation_additions-0.type'      : 'RecipeAddition',
            'fermentation_additions-0.use'       : 'SECONDARY',
            'fermentation_additions-0.amount'    : 1,
            'fermentation_additions-0.addition'  : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'SECONDARY'

    def test_schema_failure(self):
        model.RecipeAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            fermentable = model.Fermentable(
                name        = '2-Row',
                origin      = 'US',
                ppg         = 36,
                lovibond    = 2
            ),
            amount      = 12,
            unit        = 'POUND',
            use         = 'MASH'
        )
        model.commit()
       
        params = {
            'additions-0.type'          : 'RecipeAddition',
            'additions-0.amount'        : '10 lb',
            'additions-0.use'           : 'MASH',
            'additions-0.addition'      : 1
        }            

        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params=copy, status=200)
            assert response.status_int == 200

        a = model.RecipeAddition.get(1)
        assert a.amount == 12
        assert a.unit == 'POUND'

    def test_hop_schema_failure(self):
        model.HopAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            hop         = model.Hop(name = 'Cascade', alpha_acid=5.5, origin = 'US'),
            amount      = 0.0625,
            unit        = 'POUND',
            use         = 'BOIL',
            duration    = timedelta(minutes=60),
            form        = 'PELLET',
            alpha_acid  = 5.5
        )
        model.commit()
       
        params = {
            'additions-0.type'          : 'HopAddition',
            'additions-0.amount'        : '2 oz',
            'additions-0.use'           : 'BOIL',
            'additions-0.addition'      : 1,
            'additions-0.form'          : 'LEAF',
            'additions-0.alpha_acid'    : 7
        }            

        for k in params:
            copy = params.copy()
            del copy[k]

            response = self.put('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients', params=copy, status=200)
            assert response.status_int == 200

        a = model.HopAddition.get(1)
        assert a.amount == 0.0625
        assert a.unit == 'POUND'
        assert a.form == 'PELLET'
        assert a.alpha_acid == 5.5


class TestRecipeRemoval(TestAuthenticatedApp):

    def test_addition_removal(self):
        model.RecipeAddition(
            recipe      = model.Recipe(
                name='Rocky Mountain River IPA', 
                author=model.User.get(1)
            ),
            fermentable = model.Fermentable(name = '2-Row', origin='US'),
            amount      = 12,
            unit        = 'POUND',
            use         = 'MASH'
        )
        model.commit()

        self.delete('/recipes/1/rocky-mountain-river-ipa/builder/async/ingredients/1')

        assert model.RecipeAddition.query.count() == 0


class TestAuthenticatedUserRecipeLookup(TestAuthenticatedApp):

    def test_lookup(self):
        """
        If the recipe has an author, and we're logged in as that author,
        we should have access to edit the recipe.
        """
        model.Recipe(
            name    = 'American IPA',
            slugs   = [
                model.RecipeSlug(name = 'American IPA'),
                model.RecipeSlug(name = 'American IPA (Revised)')
            ],
            author  = model.User.get(1)
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
            name    = 'American IPA',
            slugs   = [
                model.RecipeSlug(name = 'American IPA')
            ]
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
            name    = 'American IPA',
            slugs   = [
                model.RecipeSlug(name = 'American IPA')
            ],
            author  = model.User()
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
            name    = 'American IPA',
            slugs   = [
                model.RecipeSlug(name = 'American IPA')
            ],
            author  = model.User.get(1)
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401

    def test_unauthorized_lookup_trial_user(self):
        """
        If the recipe is a trial recipe, but is not *our* trial recipe,
        we should *not* have access to edit the recipe.
        """
        model.Recipe(
            name    = 'American IPA',
            slugs   = [
                model.RecipeSlug(name = 'American IPA')
            ]
        )
        model.commit()

        response = self.get('/recipes/1/american-ipa/builder/', status=401)
        assert response.status_int == 401
