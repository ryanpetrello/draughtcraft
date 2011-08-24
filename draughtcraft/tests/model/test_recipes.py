from draughtcraft       import model
from draughtcraft.tests import TestModel
from datetime           import timedelta
from copy               import deepcopy


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

    def test_printable_hop_amount(self):
        addition = model.HopAddition(
            amount  = 0.0625, # 1 oz
            unit    = 'POUND'
        )

        assert addition.printable_amount == '1 oz'

        addition = model.HopAddition(
            amount  = 0,
            unit    = 'POUND'
        )

        assert addition.printable_amount == '0 oz'

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

    def test_minutes(self):
        a = model.RecipeAddition()
        assert a.minutes == 0

        a.duration = timedelta(seconds=120)
        assert a.minutes == 2


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

        assert recipe.contains(f1, 'invalid') is False
        assert recipe.contains(h1, 'invalid') is False
        assert recipe.contains(h2, 'invalid') is False
        assert recipe.contains(h3, 'invalid') is False
        assert recipe.contains(h4, 'invalid') is False
        assert recipe.contains(h5, 'invalid') is False
        assert recipe.contains(y1, 'invalid') is False
        assert recipe.contains(y2, 'invalid') is False

    def test_next_fermentation_step(self):
        recipe = model.Recipe()
        recipe.fermentation_steps.append(
            model.FermentationStep(
                step = 'PRIMARY',
                days = 7,
                fahrenheit = 50
            )
        )

        assert recipe.next_fermentation_step == 'SECONDARY'

        recipe.fermentation_steps.append(
            model.FermentationStep(
                step = 'SECONDARY',
                days = 14,
                fahrenheit = 35
            )
        )

        assert recipe.next_fermentation_step == 'TERTIARY'

        recipe.fermentation_steps.append(
            model.FermentationStep(
                step = 'TERTIARY',
                days = 31,
                fahrenheit = 35
            )
        )

        assert recipe.next_fermentation_step == None

    def test_url(self):
        recipe = model.Recipe(
            id      = 1,
            name    = u'Rocky Mountain River IPA'
        )        
        assert recipe.url() == '/recipes/1/rocky-mountain-river-ipa/'
        assert recipe.url(False) == '/recipes/1/rocky-mountain-river-ipa/builder/'

    def test_printable_type(self):
        assert model.Recipe(
            type = u'MASH'
        ).printable_type == 'All Grain'
        assert model.Recipe(
            type = u'EXTRACT'
        ).printable_type == 'Extract'
        assert model.Recipe(
            type = u'EXTRACTSTEEP'
        ).printable_type == 'Extract with Steeped Grains'
        assert model.Recipe(
            type = u'MINIMASH'
        ).printable_type == 'Extract with Mini-Mash'


class TestFermentationStep(object):

    def test_fermentation_step(self):
        recipe = model.Recipe()
        recipe.fermentation_steps.extend([
            model.FermentationStep(
                step = 'PRIMARY',
                days = 7,
                fahrenheit = 50
            ),
            model.FermentationStep(
                step = 'SECONDARY',
                days = 14,
                fahrenheit = 35
            ),
            model.FermentationStep(
                step = 'TERTIARY',
                days = 31,
                fahrenheit = 35
            )
        ])

        steps = recipe.fermentation_steps
        assert steps[0].step == 'PRIMARY'
        assert steps[0].days == 7
        assert steps[0].fahrenheit == 50
        assert steps[0].recipe == recipe

        assert steps[1].step == 'SECONDARY'
        assert steps[1].days == 14
        assert steps[1].fahrenheit == 35
        assert steps[1].recipe == recipe

        assert steps[2].step == 'TERTIARY'
        assert steps[2].days == 31
        assert steps[2].fahrenheit == 35
        assert steps[2].recipe == recipe


class TestRecipeCopy(TestModel):

    def test_simple_copy(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        deepcopy(recipe)
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeSlug.query.count() == 2

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)

        assert r1.type == r2.type == 'MASH'
        assert r1.name == r2.name == 'Rocky Mountain River IPA'
        assert r1.gallons == r2.gallons == 5
        assert r1.boil_minutes == r2.boil_minutes == 60
        assert r1.notes == r2.notes == u'This is my favorite recipe.'

        assert len(r1.slugs) == len(r2.slugs) == 1
        assert r1.slugs[0] != r2.slugs[0]
        assert r1.slugs[0].slug == r2.slugs[0].slug == 'rocky-mountain-river-ipa'

    def test_author_copy(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User()
        )
        model.commit()

        recipe = model.Recipe.query.first()
        deepcopy(recipe)
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.User.query.count() == 1

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert r1.author == r2.author == model.User.get(1)

    def test_style_copy(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            style   = model.Style(name = u'American IPA')
        )
        model.commit()

        recipe = model.Recipe.query.first()
        deepcopy(recipe)
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.Style.query.count() == 1

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert r1.style == r2.style == model.Style.get(1)

    def test_slugs_copy(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            slugs   = [
                model.RecipeSlug(slug=u'rocky-mountain-river-ipa'),
                model.RecipeSlug(slug=u'my-favorite-ipa')
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        deepcopy(recipe)
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeSlug.query.count() == 4

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.slugs) == len(r2.slugs) == 2

        assert r1.slugs[0] != r2.slugs[0]
        assert r1.slugs[0].slug == r2.slugs[0].slug == 'rocky-mountain-river-ipa'

        assert r1.slugs[1] != r2.slugs[1]
        assert r1.slugs[1].slug == r2.slugs[1].slug == 'my-favorite-ipa'

    def test_fermentation_steps_copy(self):
        model.Recipe(
            name                    = 'Rocky Mountain River IPA',
            fermentation_steps      = [
                model.FermentationStep(
                    step        = 'PRIMARY',
                    days        = 14,
                    fahrenheit  = 65
                ),
                model.FermentationStep(
                    step        = 'SECONDARY',
                    days        = 90,
                    fahrenheit  = 45
                )
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        deepcopy(recipe)
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.FermentationStep.query.count() == 4

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.fermentation_steps) == len(r2.fermentation_steps) == 2
        
        assert r1.fermentation_steps[0].step == r2.fermentation_steps[0].step == 'PRIMARY'
        assert r1.fermentation_steps[0].days == r2.fermentation_steps[0].days == 14
        assert r1.fermentation_steps[0].fahrenheit == r2.fermentation_steps[0].fahrenheit == 65

        assert r1.fermentation_steps[1].step == r2.fermentation_steps[1].step == 'SECONDARY'
        assert r1.fermentation_steps[1].days == r2.fermentation_steps[1].days == 90
        assert r1.fermentation_steps[1].fahrenheit == r2.fermentation_steps[1].fahrenheit == 45
