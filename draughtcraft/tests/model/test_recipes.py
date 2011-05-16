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

    def test_percentage(self):
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

        assert a1.percentage == .75
        assert a2.percentage == .25
        assert a3.percentage == .75
        assert a4.percentage == .25

    def test_zero_percentage(self):
        recipe = model.Recipe()
        
        a1 = model.RecipeAddition(
            use         = 'MASH',
            amount      = 0,
            unit        = 'POUND',
            fermentable = model.Fermentable()
        )
        a2 = model.RecipeAddition(
            use         = 'MASH',
            amount      = 0,
            unit        = 'POUND',
            fermentable = model.Fermentable()
        )
        recipe.additions = [a1, a2]

        assert a1.percentage == 0
        assert a2.percentage == 0


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

    def test_recipe_contains(self):
        recipe = model.Recipe()

        f1 = model.Fermentable()
        h1 = model.Hop()
        h2 = model.Hop()
        h3 = model.Hop()
        h4 = model.Hop()
        h5 = model.Hop()
        y1 = model.Yeast()
        y2 = model.Yeast()

        recipe.additions = [
            model.RecipeAddition(
                use         = 'MASH',
                fermentable = f1
            ),
            model.RecipeAddition(
                use         = 'MASH',
                hop         = h1
            ),
            model.RecipeAddition(
                use         = 'FIRST WORT',
                hop         = h2
            ),
            model.RecipeAddition(
                use         = 'BOIL',
                hop         = h3
            ),
            model.RecipeAddition(
                use         = 'POST-BOIL',
                hop         = h4
            ),
            model.RecipeAddition(
                use         = 'FLAME OUT',
                hop         = h5
            ),
            model.RecipeAddition(
                use         = 'PRIMARY',
                yeast       = y1
            ),
            model.RecipeAddition(
                use         = 'SECONDARY',
                yeast       = y2
            )
        ]

        assert recipe.contains(f1, 'mash')
        assert recipe.contains(f1, 'boil') is False
        assert recipe.contains(f1, 'fermentation') is False

        assert recipe.contains(h1, 'mash')
        assert recipe.contains(h1, 'boil') is False
        assert recipe.contains(h1, 'fermentation') is False

        assert recipe.contains(h2, 'mash') is False
        assert recipe.contains(h2, 'boil')
        assert recipe.contains(h2, 'fermentation') is False

        assert recipe.contains(h3, 'mash') is False
        assert recipe.contains(h3, 'boil')
        assert recipe.contains(h3, 'fermentation') is False

        assert recipe.contains(h4, 'mash') is False
        assert recipe.contains(h4, 'boil')
        assert recipe.contains(h4, 'fermentation') is False

        assert recipe.contains(h5, 'mash') is False
        assert recipe.contains(h5, 'boil')
        assert recipe.contains(h5, 'fermentation') is False

        assert recipe.contains(y1, 'mash') is False
        assert recipe.contains(y1, 'boil') is False
        assert recipe.contains(y1, 'fermentation')

        assert recipe.contains(y2, 'mash') is False
        assert recipe.contains(y2, 'boil') is False
        assert recipe.contains(y2, 'fermentation')
