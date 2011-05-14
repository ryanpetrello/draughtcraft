from draughtcraft       import model


class TestRecipeAddition(object):

    def test_fermentable_ingredient(self): 
        addition = model.RecipeAddition()
        fermentable = model.Fermentable()

        addition.fermentable = fermentable

        assert addition.ingredient == fermentable

    def test_hop_ingredient(self): 
        addition = model.RecipeAddition()
        hop = model.Hop()

        addition.hop = hop

        assert addition.ingredient == hop

    def test_yeast_ingredient(self): 
        addition = model.RecipeAddition()
        yeast = model.Yeast()

        addition.yeast = yeast

        assert addition.ingredient == yeast

    def test_printable_amount(self):
        addition = model.RecipeAddition(
            amount  = 5,
            unit    = 'POUND'
        )

        assert addition.printable_amount == '5 lb'

    def test_percentage_for(self):
        recipe = model.Recipe()
        
        a1 = model.RecipeAddition(
            use         = 'MASH',
            amount      = 6,
            unit        = 'POUND',
            fermentable = model.Fermentable()
        )
        a2 = model.RecipeAddition(
            use         = 'MASH',
            amount      = 2,
            unit        = 'POUND',
            fermentable = model.Fermentable()
        )
        a3 = model.RecipeAddition(
            use         = 'BOIL',
            amount      = .046875, # .75 oz
            unit        = 'POUND',
            hop         = model.Hop()
        )
        a4 = model.RecipeAddition(
            use         = 'BOIL',
            amount      = .015625, # .25 oz
            unit        = 'POUND',
            hop         = model.Hop()
        )
        recipe.additions = [a1, a2, a3, a4]

        assert a1.percentage_for('mash') == .75
        assert a2.percentage_for('mash') == .25
        assert a1.percentage_for('boil') == 0
        assert a2.percentage_for('boil') == 0
        assert a3.percentage_for('boil') == .75
        assert a4.percentage_for('boil') == .25
        assert a3.percentage_for('mash') == 0
        assert a4.percentage_for('mash') == 0

        assert a1.percentage_for('invalid') == 0
        assert a2.percentage_for('invalid') == 0
        assert a3.percentage_for('invalid') == 0
        assert a4.percentage_for('invalid') == 0


class TestRecipe(object):

    def test_recipe_components(self):
        recipe = model.Recipe()

        recipe.additions = [
            model.RecipeAddition(
                use         = 'MASH',
                fermentable = model.Fermentable()
            ),
            model.RecipeAddition(
                use         = 'MASH',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'FIRST WORT',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'BOIL',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'POST-BOIL',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'FLAME OUT',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'PRIMARY',
                yeast       = model.Yeast()
            ),
            model.RecipeAddition(
                use         = 'SECONDARY',
                yeast       = model.Yeast()
            )
        ]

        assert len(recipe.mash[model.Fermentable]) == 1
        assert len(recipe.mash[model.Hop]) == 1
        assert len(recipe.boil[model.Hop]) == 4
        assert len(recipe.fermentation[model.Yeast]) == 2

    def test_ingredient_partition(self):
        recipe = model.Recipe()
        recipe.additions = [
            model.RecipeAddition(
                use         = 'MASH',
                fermentable = model.Fermentable()
            ),
            model.RecipeAddition(
                use         = 'MASH',
                hop         = model.Hop()
            )
        ]
        partitions = recipe._partition(recipe.additions)
        assert len(partitions[model.Fermentable]) == 1
        assert len(partitions[model.Hop]) == 1

        recipe.additions = [
            model.RecipeAddition(
                use         = 'FIRST WORT',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'BOIL',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'POST-BOIL',
                hop         = model.Hop()
            ),
            model.RecipeAddition(
                use         = 'FLAME OUT',
                hop         = model.Hop()
            )
        ]
        partitions = recipe._partition(recipe.additions)
        assert len(partitions[model.Hop]) == 4

        recipe.additions = [
            model.RecipeAddition(
                use         = 'PRIMARY',
                yeast       = model.Yeast()
            ),
            model.RecipeAddition(
                use         = 'SECONDARY',
                yeast       = model.Yeast()
            )
        ]
        partitions = recipe._partition(recipe.additions)
        assert len(partitions[model.Yeast]) == 2

    def test_ingredient_percent(self):
        recipe = model.Recipe()
        
        a1 = model.RecipeAddition(
            use         = 'MASH',
            amount      = 6,
            unit        = 'POUND',
            fermentable = model.Fermentable()
        )
        a2 = model.RecipeAddition(
            use         = 'MASH',
            amount      = 2,
            unit        = 'POUND',
            fermentable = model.Fermentable()
        )
        a3 = model.RecipeAddition(
            use         = 'MASH',
            amount      = .046875, # .75 oz
            unit        = 'POUND',
            hop         = model.Hop()
        )
        a4 = model.RecipeAddition(
            use         = 'MASH',
            amount      = .015625, # .25 oz
            unit        = 'POUND',
            hop         = model.Hop()
        )

        percent = recipe._percent({
            'Fermentable'   : [a1, a2],
            'Hop'           : [a3, a4]
        })

        assert percent[a1] == .75
        assert percent[a2] == .25
        assert percent[a3] == .75
        assert percent[a4] == .25
