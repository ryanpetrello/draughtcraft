from draughtcraft.tests     import TestApp
from draughtcraft           import model
from datetime               import timedelta

class TestRecipeBuilder(TestApp):

    def test_recipe_create(self):
        assert model.Recipe.query.count() == 0

        response = self.get('/recipes/create')
        assert response.status_int == 302

        assert model.Recipe.query.count() == 1
        assert response.headers['Location'].endswith('/recipes/1/builder')

    def test_recipe_missing(self):
        response = self.get('/recipes/1', status=404)
        assert response.status_int == 404


class TestMashAdditions(TestApp):

    def test_fermentable(self):
        model.Recipe()
        model.Fermentable(name = '2-Row', origin='US')
        model.commit()

        self.post('/recipes/1/builder/async', params={
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
        model.Recipe()
        model.Hop(name = 'Cascade')
        model.commit()

        self.post('/recipes/1/builder/async', params={
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
        model.Recipe()
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

            response = self.post('/recipes/1/builder/async', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestBoilAdditions(TestApp):

    def test_fermentable(self):
        model.Recipe()
        model.Fermentable(name = '2-Row', origin='US')
        model.commit()

        self.post('/recipes/1/builder/async', params={
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
        model.Recipe()
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5
        )
        model.commit()

        self.post('/recipes/1/builder/async', params={
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
        model.Recipe()
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

            response = self.post('/recipes/1/builder/async', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestFermentationAdditions(TestApp):

    def test_hop(self):
        model.Recipe()
        model.Hop(
            name        = 'Cascade', 
            alpha_acid  = 5.5
        )
        model.commit()

        self.post('/recipes/1/builder/async', params={
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
        model.Recipe()
        model.Yeast(
            name = 'Wyeast 1056 - American Ale',
            form = 'LIQUID'
        )
        model.commit()

        self.post('/recipes/1/builder/async', params={
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
        model.Recipe()
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

            response = self.post('/recipes/1/builder/async', params=copy, status=400)
            assert response.status_int == 400

        assert model.RecipeAddition.query.count() == 0


class TestRecipeChange(TestApp):

    def test_mash_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(),
            fermentable = model.Fermentable(name = '2-Row', origin='US'),
            amount      = 12,
            unit        = 'POUND',
            use         = 'MASH'
        )
        model.commit()

        self.put('/recipes/1/builder/async', params={
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

    def test_boil_hop_change(self):
        model.HopAddition(
            recipe      = model.Recipe(),
            hop         = model.Hop(name = 'Cascade'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.HopAddition(
            recipe      = model.Recipe(),
            hop         = model.Hop(name = 'Centennial'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=60),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.commit()

        self.put('/recipes/1/builder/async', params={
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

    def test_yeast_change(self):
        model.RecipeAddition(
            recipe      = model.Recipe(),
            yeast       = model.Yeast(
                name = 'Wyeast 1056 - American Ale',
                form = 'LIQUID'
            ),
            amount      = 1,
            use         = 'PRIMARY'
        )
        model.commit()

        self.put('/recipes/1/builder/async', params={
            'additions-0.type'      : 'RecipeAddition',
            'additions-0.use'       : 'SECONDARY',
            'additions-0.amount'    : 1,
            'additions-0.addition'  : 1
        })

        a = model.RecipeAddition.get(1)
        assert a.use == 'SECONDARY'

    def test_schema_failure(self):
        model.RecipeAddition(
            recipe      = model.Recipe(),
            fermentable = model.Fermentable(name = '2-Row', origin='US'),
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

            response = self.put('/recipes/1/builder/async', params=copy, status=400)
            assert response.status_int == 400

        a = model.RecipeAddition.get(1)
        assert a.amount == 12
        assert a.unit == 'POUND'

    def test_hop_schema_failure(self):
        model.HopAddition(
            recipe      = model.Recipe(),
            hop         = model.Hop(name = 'Cascade', alpha_acid=5.5),
            amount      = 0.0625,
            unit        = 'POUND',
            use         = 'BOIL',
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

            response = self.put('/recipes/1/builder/async', params=copy, status=400)
            assert response.status_int == 400

        a = model.HopAddition.get(1)
        assert a.amount == 0.0625
        assert a.unit == 'POUND'
        assert a.form == 'PELLET'
        assert a.alpha_acid == 5.5


class TestRecipeRemoval(TestApp):

    def test_addition_removal(self):
        model.RecipeAddition(
            recipe      = model.Recipe(),
            fermentable = model.Fermentable(name = '2-Row', origin='US'),
            amount      = 12,
            unit        = 'POUND',
            use         = 'MASH'
        )
        model.commit()

        self.delete('/recipes/1/builder/async/1')

        assert model.RecipeAddition.query.count() == 0
