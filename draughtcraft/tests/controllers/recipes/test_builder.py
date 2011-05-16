from draughtcraft.tests     import TestApp
from draughtcraft           import model

class TestRecipeBuilder(TestApp):

    def test_recipe_create(self):
        assert model.Recipe.query.count() == 0

        response = self.get('/recipes/create')
        assert response.status_int == 302

        assert model.Recipe.query.count() == 1
        assert response.headers['Location'].endswith('/recipes/1/builder')

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
