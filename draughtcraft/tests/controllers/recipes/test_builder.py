from draughtcraft.tests     import TestApp
from draughtcraft           import model
from datetime               import timedelta


class TestMashAdditions(TestApp):

    def test_fermentable(self):
        model.Recipe(name='Rocky Mountain River IPA')
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
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
        model.Recipe(name='Rocky Mountain River IPA')
        model.Hop(name = 'Cascade')
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
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
        model.Recipe(name="Rocky Mountain River IPA")
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

            response = self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestBoilAdditions(TestApp):

    def test_fermentable(self):
        model.Recipe(name="Rocky Mountain River IPA")
        model.Fermentable(
            name        = '2-Row',
            origin      = 'US',
            ppg         = 36,
            lovibond    = 2
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
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
        model.Recipe(name="Rocky Mountain River IPA")
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
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
        model.Recipe(name="Rocky Mountain River IPA")
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

            response = self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestFermentationAdditions(TestApp):

    def test_hop(self):
        model.Recipe(name="Rocky Mountain River IPA")
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
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
        model.Recipe(name="Rocky Mountain River IPA")
        model.Yeast(
            name = 'Wyeast 1056 - American Ale',
            form = 'LIQUID',
            attenuation = .75
        )
        model.commit()

        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
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
        model.Recipe(name="Rocky Mountain River IPA")
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

            response = self.post('/recipes/1/rocky-mountain-river-ipa/builder/async', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestRecipeSettings(TestApp):

    def test_style_change(self):
        model.Recipe(name="Rocky Mountain River IPA")
        model.Style(name = u'American Ale')
        model.commit()

        assert model.Recipe.get(1).style is None
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/style', params={
            'target': 1
        })
        
        assert model.Recipe.get(1).style == model.Style.get(1)

    def test_style_remove(self):
        recipe = model.Recipe(name="Rocky Mountain River IPA")
        recipe.style = model.Style(name = u'American Ale')
        model.commit()

        assert model.Recipe.get(1).style == model.Style.get(1)
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/style', params={
            'target': '' 
        })
        
        assert model.Recipe.get(1).style is None

    def test_volume_change(self):
        model.Recipe(name="Rocky Mountain River IPA")
        model.commit()

        assert model.Recipe.get(1).gallons == 5.0
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/volume', params={
            'volume'    : 10.0,
            'unit'      : 'GALLON' 
        })
        
        assert model.Recipe.get(1).gallons == 10.0

    def test_notes_update(self):
        model.Recipe(name="Rocky Mountain River IPA")
        model.commit()

        assert model.Recipe.get(1).notes is None
        self.post('/recipes/1/rocky-mountain-river-ipa/builder/async/settings/notes', params={
            'notes'    : u'Testing 1 2 3...'
        })
        
        assert model.Recipe.get(1).notes == u'Testing 1 2 3...'


class TestFermentationStepChange(TestApp):

    def test_fermentation_step_add(self):
        recipe = model.Recipe(
            name        = u'Rocky Mountain River IPA'
        )
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
        recipe = model.Recipe(
            name        = u'Rocky Mountain River IPA'
        )
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
        assert len(recipe.fermentation_steps) == 1
        assert recipe.fermentation_steps[0].step == 'PRIMARY'
        assert recipe.fermentation_steps[0].days == 14
        assert recipe.fermentation_steps[0].fahrenheit == 68

    def test_fermentation_step_delete(self):
        recipe = model.Recipe(
            name        = u'Rocky Mountain River IPA'
        )
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


class TestRecipeChange(TestApp):

    def test_mash_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
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

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
            'additions-0.type'          : 'RecipeAddition',
            'additions-0.amount'        : '10 lb',
            'additions-0.use'           : 'MASH',
            'additions-0.addition'      : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'MASH'
        assert a.amount == 10
        assert a.unit == 'POUND'
        assert a.ingredient == model.Fermentable.get(1)

    def test_unitless_mash_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
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
        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
            'additions-0.type'          : 'RecipeAddition',
            'additions-0.amount'        : '5',
            'additions-0.use'           : 'MASH',
            'additions-0.addition'      : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'MASH'
        assert a.amount == 5
        assert a.unit == 'POUND'
        assert a.ingredient == model.Fermentable.get(1)

    def test_boil_hop_change(self):
        model.HopAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            hop         = model.Hop(name = 'Cascade'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.HopAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            hop         = model.Hop(name = 'Centennial'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=60),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
            'additions-0.type'          : 'HopAddition',
            'additions-0.amount'        : '2 oz',
            'additions-0.use'           : 'BOIL',
            'additions-0.alpha_acid'    : 7,
            'additions-0.duration'      : 10,
            'additions-0.addition'      : 1,
            'additions-0.form'          : 'PELLET',
            'additions-1.type'          : 'HopAddition',
            'additions-1.amount'        : '.5 oz',
            'additions-1.use'           : 'BOIL',
            'additions-1.alpha_acid'    : 4,
            'additions-1.duration'      : 45,
            'additions-1.addition'      : 2,
            'additions-1.form'          : 'PLUG'
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
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            hop         = model.Hop(name = 'Cascade'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
            'additions-0.type'          : 'HopAddition',
            'additions-0.amount'        : '2 oz',
            'additions-0.use'           : 'FIRST WORT',
            'additions-0.alpha_acid'    : 7,
            'additions-0.duration'      : 30,
            'additions-0.addition'      : 1,
            'additions-0.form'          : 'PELLET'
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
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            hop         = model.Hop(name = 'Cascade'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
            'additions-0.type'          : 'HopAddition',
            'additions-0.amount'        : '2 oz',
            'additions-0.use'           : 'FLAME OUT',
            'additions-0.alpha_acid'    : 7,
            'additions-0.duration'      : 30,
            'additions-0.addition'      : 1,
            'additions-0.form'          : 'PELLET'
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
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            yeast       = model.Yeast(
                name = 'Wyeast 1056 - American Ale',
                form = 'LIQUID',
                attenuation = .75
            ),
            amount      = 1,
            use         = 'PRIMARY'
        )
        model.commit()

        self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params={
            'additions-0.type'      : 'RecipeAddition',
            'additions-0.use'       : 'SECONDARY',
            'additions-0.amount'    : 1,
            'additions-0.addition'  : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'SECONDARY'

    def test_schema_failure(self):
        model.RecipeAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
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

            response = self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params=copy, status=200)
            assert response.status_int == 200

        a = model.RecipeAddition.get(1)
        assert a.amount == 12
        assert a.unit == 'POUND'

    def test_hop_schema_failure(self):
        model.HopAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            hop         = model.Hop(name = 'Cascade', alpha_acid=5.5),
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

            response = self.put('/recipes/1/rocky-mountain-river-ipa/builder/async', params=copy, status=200)
            assert response.status_int == 200

        a = model.HopAddition.get(1)
        assert a.amount == 0.0625
        assert a.unit == 'POUND'
        assert a.form == 'PELLET'
        assert a.alpha_acid == 5.5


class TestRecipeRemoval(TestApp):

    def test_addition_removal(self):
        model.RecipeAddition(
            recipe      = model.Recipe(name="Rocky Mountain River IPA"),
            fermentable = model.Fermentable(name = '2-Row', origin='US'),
            amount      = 12,
            unit        = 'POUND',
            use         = 'MASH'
        )
        model.commit()

        self.delete('/recipes/1/rocky-mountain-river-ipa/builder/async/1')

        assert model.RecipeAddition.query.count() == 0
