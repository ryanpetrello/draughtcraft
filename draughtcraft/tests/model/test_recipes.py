from draughtcraft       import model
from draughtcraft.tests import TestModel
from datetime           import timedelta

import unittest


class TestRecipeAddition(unittest.TestCase):

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


class TestRecipe(unittest.TestCase):

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

    def test_efficiency(self):
        assert model.Recipe().efficiency == .75

        user = model.User()
        model.UserSetting(
            user = user,
            name = 'brewhouse_efficiency',
            value = .80
        )
        assert model.Recipe(author = user).efficiency == .80

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
        ).printable_type == 'Mini-Mash'


class TestFermentationStep(unittest.TestCase):

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
        recipe.duplicate()
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

    def test_simple_copy_with_overrides(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.'
        )
        model.commit()

        recipe = model.Recipe.query.first()
        recipe.duplicate({
            'type'          : 'EXTRACT',
            'name'          : 'Simcoe IPA',
            'gallons'       : 10,
            'boil_minutes'  : 90,
            'notes'         : u'This is a duplicate.'
        })
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeSlug.query.count() == 2

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)

        assert r2.type == 'EXTRACT'
        assert r2.name == 'Simcoe IPA'
        assert r2.gallons == 10
        assert r2.boil_minutes == 90
        assert r2.notes == u'This is a duplicate.'

    def test_author_copy(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User()
        )
        model.commit()

        recipe = model.Recipe.query.first()
        recipe.duplicate()
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.User.query.count() == 1

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert r1.author == r2.author == model.User.get(1)

    def test_author_copy_with_overrides(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            author  = model.User()
        )
        model.commit()

        recipe = model.Recipe.query.first()
        recipe.duplicate({
            'author' : model.User()
        })
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.User.query.count() == 2

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert r1.author and r2.author
        assert r1.author != r2.author

    def test_style_copy(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            style   = model.Style(name = u'American IPA')
        )
        model.commit()

        recipe = model.Recipe.query.first()
        recipe.duplicate()
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.Style.query.count() == 1

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert r1.style == r2.style == model.Style.get(1)

    def test_style_copy_with_overrides(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            style   = model.Style(name = u'American IPA')
        )
        model.commit()

        recipe = model.Recipe.query.first()
        recipe.duplicate({
            'style' : model.Style(name = u'Baltic Porter')
        })
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.Style.query.count() == 2

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert r1.style and r2.style
        assert r1.style != r2.style

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
        recipe.duplicate()
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeSlug.query.count() == 4

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.slugs) == len(r2.slugs) == 2

        assert r1.slugs[0] != r2.slugs[0]
        assert r1.slugs[0].slug == r2.slugs[0].slug == 'rocky-mountain-river-ipa'

        assert r1.slugs[1] != r2.slugs[1]
        assert r1.slugs[1].slug == r2.slugs[1].slug == 'my-favorite-ipa'

    def test_slugs_copy_with_overrides(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            slugs   = [
                model.RecipeSlug(slug=u'rocky-mountain-river-ipa'),
                model.RecipeSlug(slug=u'my-favorite-ipa')
            ]
        )
        model.commit()

        recipe = model.Recipe.query.first()
        recipe.duplicate({
            'slugs': [model.RecipeSlug(slug='custom-slug')]
        })
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeSlug.query.count() == 3

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.slugs) == 2
        assert len(r2.slugs) == 1

        assert r1.slugs[0].slug == 'rocky-mountain-river-ipa'
        assert r1.slugs[1].slug == 'my-favorite-ipa'
        assert r2.slugs[0].slug == 'custom-slug'

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
        recipe.duplicate()
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

    def test_fermentation_steps_copy_with_override(self):
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
        recipe.duplicate({
            'fermentation_steps' : [model.FermentationStep(
                step        = 'PRIMARY',
                days        = 21,
                fahrenheit  = 75
            )]
        })
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.FermentationStep.query.count() == 3

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.fermentation_steps) == 2
        assert len(r2.fermentation_steps) == 1
        
        assert r2.fermentation_steps[0].step == 'PRIMARY'
        assert r2.fermentation_steps[0].days == 21
        assert r2.fermentation_steps[0].fahrenheit == 75

    def test_additions_copy(self):
        recipe = model.Recipe(name = u'Sample Recipe')

        grain           = model.Fermentable()
        primary_hop     = model.Hop()
        bittering_hop   = model.Hop()
        yeast           = model.Yeast()
        recipe.additions = [
            model.RecipeAddition(
                use         = 'MASH',
                fermentable = grain
            ),
            model.RecipeAddition(
                use         = 'MASH',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'FIRST WORT',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'BOIL',
                hop         = primary_hop,
            ),
            model.RecipeAddition(
                use         = 'POST-BOIL',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'FLAME OUT',
                hop         = bittering_hop
            ),
            model.RecipeAddition(
                use         = 'PRIMARY',
                yeast       = yeast
            ),
            model.RecipeAddition(
                use         = 'SECONDARY',
                yeast       = yeast
            )
        ]
        model.commit()

        assert model.Recipe.query.count() == 1
        assert model.RecipeAddition.query.count() == 8
        assert model.Fermentable.query.count() == 1
        assert model.Hop.query.count() == 2
        assert model.Yeast.query.count() == 1

        recipe = model.Recipe.query.first()
        recipe.duplicate()
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeAddition.query.count() == 16
        assert model.Fermentable.query.count() == 1
        assert model.Hop.query.count() == 2
        assert model.Yeast.query.count() == 1

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.additions) == len(r2.additions) == 8

        assert r1.additions[0].fermentable == r2.additions[0].fermentable == model.Fermentable.query.first()
        assert r1.additions[1].hop == r2.additions[1].hop == model.Hop.query.first()
        assert r1.additions[2].hop == r2.additions[2].hop == model.Hop.query.first()
        assert r1.additions[3].hop == r2.additions[3].hop == model.Hop.query.first()
        assert r1.additions[4].hop == r2.additions[4].hop == model.Hop.query.first()
        assert r1.additions[5].hop == r2.additions[5].hop == model.Hop.query.all()[-1]
        assert r1.additions[6].yeast == r2.additions[6].yeast == model.Yeast.query.first()
        assert r1.additions[7].yeast == r2.additions[7].yeast == model.Yeast.query.all()[-1]

    def test_additions_copy_with_overrides(self):
        recipe = model.Recipe(name = u'Sample Recipe')

        grain           = model.Fermentable()
        primary_hop     = model.Hop()
        bittering_hop   = model.Hop()
        yeast           = model.Yeast()
        recipe.additions = [
            model.RecipeAddition(
                use         = 'MASH',
                fermentable = grain
            ),
            model.RecipeAddition(
                use         = 'MASH',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'FIRST WORT',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'BOIL',
                hop         = primary_hop,
            ),
            model.RecipeAddition(
                use         = 'POST-BOIL',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'FLAME OUT',
                hop         = bittering_hop
            ),
            model.RecipeAddition(
                use         = 'PRIMARY',
                yeast       = yeast
            ),
            model.RecipeAddition(
                use         = 'SECONDARY',
                yeast       = yeast
            )
        ]
        model.commit()

        assert model.Recipe.query.count() == 1
        assert model.RecipeAddition.query.count() == 8
        assert model.Fermentable.query.count() == 1
        assert model.Hop.query.count() == 2
        assert model.Yeast.query.count() == 1

        recipe = model.Recipe.query.first()
        recipe.duplicate({
            'additions' : [model.RecipeAddition(
                use         = 'MASH',
                fermentable = model.Fermentable.query.first()
            )]
        })
        model.commit()

        assert model.Recipe.query.count() == 2
        assert model.RecipeAddition.query.count() == 9
        assert model.Fermentable.query.count() == 1
        assert model.Hop.query.count() == 2
        assert model.Yeast.query.count() == 1

        r1, r2 = model.Recipe.get(1), model.Recipe.get(2)
        assert len(r1.additions) == 8
        assert len(r2.additions) == 1

        assert r2.additions[0].fermentable == model.Fermentable.query.first()


class TestDrafts(TestModel):

    def test_draft_creation(self):
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            state           = u'PUBLISHED'
        )
        model.commit()

        model.Recipe.query.first().draft()
        model.commit()

        assert model.Recipe.query.count() == 2
        source = model.Recipe.query.filter(model.Recipe.published_version == None).first()
        draft = model.Recipe.query.filter(model.Recipe.published_version != None).first()

        assert source != draft
        assert source.type == draft.type == 'MASH'
        assert source.name == draft.name == 'Rocky Mountain River IPA'
        assert source.state != draft.state
        assert draft.state == 'DRAFT'

        assert draft.published_version == source
        assert source.current_draft == draft

    def test_draft_merge(self):
        source = model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            state           = u'PUBLISHED'
        )
        source.flush()
        primary_key = source.id
        creation_date = source.creation_date
        model.commit()

        # Make a new draft of the recipe
        model.Recipe.query.first().draft()
        model.commit()

        assert model.Recipe.query.count() == 2

        # Make a change to the draft
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.name = 'Simcoe IPA'
        draft.slugs = [model.RecipeSlug(name='simcoe-ipa')]
        draft.gallons = 10
        draft.boil_minutes = 90
        draft.notes = u'This is a modified recipe'
        model.commit()

        # Merge the draft back into its origin recipe.
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.publish()
        model.commit()

        # Make sure the remaining version is the (newly saved) draft
        assert model.Recipe.query.count() == 1
        assert model.RecipeSlug.query.count() == 1
        published = model.Recipe.query.first()

        assert published.id == primary_key
        assert published.name == 'Simcoe IPA'
        assert published.state == 'PUBLISHED' # not modified
        assert published.creation_date == creation_date # not modified
        assert len(published.slugs) == 1
        assert published.slugs[0].slug == 'simcoe-ipa'
        assert published.gallons == 10
        assert published.boil_minutes == 90
        assert published.notes == u'This is a modified recipe'

    def test_draft_merge_style(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
            style   = model.Style(name='American IPA'),
            state   = u'PUBLISHED'
        )
        model.commit()

        # Make a new draft of the recipe
        model.Recipe.query.first().draft()
        model.commit()

        assert model.Recipe.query.count() == 2

        # Change the style of the draft
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.style = model.Style(name='Baltic Porter')
        model.commit()

        # Merge the draft back into its origin recipe.
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.publish()
        model.commit()

        # Make sure the remaining version is the (newly saved) draft
        assert model.Recipe.query.count() == 1
        assert model.Style.query.count() == 2
        published = model.Recipe.query.first()

        assert published.style == model.Style.get_by(name='Baltic Porter')

    def test_draft_merge_fermentation_steps(self):
        model.Recipe(
            name    = 'Rocky Mountain River IPA',
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
            ],
            state   = u'PUBLISHED'
        )
        model.commit()

        # Make a new draft of the recipe
        model.Recipe.query.first().draft()
        model.commit()

        assert model.Recipe.query.count() == 2

        # Change the fermentation schedule of the draft
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.fermentation_steps = [model.FermentationStep(
            step        = 'PRIMARY',
            days        = 21,
            fahrenheit  = 75
        )]
        model.commit()

        # Merge the draft back into its origin recipe.
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.publish()
        model.commit()

        # Make sure the remaining version is the (newly saved) draft
        assert model.Recipe.query.count() == 1
        assert model.FermentationStep.query.count() == 1
        published = model.Recipe.query.first()
        
        assert published.fermentation_steps[0].step == 'PRIMARY'
        assert published.fermentation_steps[0].days == 21
        assert published.fermentation_steps[0].fahrenheit == 75

    def test_draft_merge_additions(self):
        recipe = model.Recipe(
            name    = 'Rocky Mountain River IPA',
            state   = u'PUBLISHED'
        )

        # Add some ingredients
        grain           = model.Fermentable()
        primary_hop     = model.Hop()
        bittering_hop   = model.Hop()
        yeast           = model.Yeast()
        recipe.additions = [
            model.RecipeAddition(
                use         = 'MASH',
                fermentable = grain
            ),
            model.RecipeAddition(
                use         = 'MASH',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'FIRST WORT',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'BOIL',
                hop         = primary_hop,
            ),
            model.RecipeAddition(
                use         = 'POST-BOIL',
                hop         = primary_hop
            ),
            model.RecipeAddition(
                use         = 'FLAME OUT',
                hop         = bittering_hop
            ),
            model.RecipeAddition(
                use         = 'PRIMARY',
                yeast       = yeast
            ),
            model.RecipeAddition(
                use         = 'SECONDARY',
                yeast       = yeast
            )
        ]
        model.commit()

        # Make a new draft of the recipe
        model.Recipe.query.first().draft()
        model.commit()

        assert model.Recipe.query.count() == 2

        # Change the ingredients of the draft
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.additions = [model.RecipeAddition(
            use         = 'MASH',
            fermentable = model.Fermentable.query.first()
        )]
        model.commit()

        # Merge the draft back into its origin recipe.
        draft = model.Recipe.query.filter(model.Recipe.state == 'DRAFT').first()
        draft.publish()
        model.commit()

        # Make sure the remaining version is the (newly saved) draft
        assert model.Recipe.query.count() == 1
        assert model.RecipeAddition.query.count() == 1
        published = model.Recipe.query.first()

        assert published.additions[0].fermentable == model.Fermentable.query.first()

    def test_simple_publish(self):
        source = model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            state           = u'DRAFT'
        )
        source.flush()
        primary_key = source.id
        model.commit()

        # Make a new draft of the recipe
        model.Recipe.query.first().publish()
        model.commit()

        assert model.Recipe.query.count() == 1
        assert model.Recipe.query.first().id == primary_key
        assert model.Recipe.query.first().state == "PUBLISHED"

    def test_statistic_caching(self):
        """
        When a recipe is published, certain statistics (like SRM) should be
        stored on a cached column so the values can be queried.
        """
        model.Recipe(
            type            = 'MASH',
            name            = 'Rocky Mountain River IPA',
            gallons         = 5,
            boil_minutes    = 60,
            notes           = u'This is my favorite recipe.',
            state           = u'DRAFT'
        )
        model.commit()

        # Make a new draft of the recipe
        recipe = model.Recipe.query.first()
        recipe.publish()
        model.commit()

        assert model.Recipe.query.first().og == 1.0
        assert model.Recipe.query.first().fg == 1.0
        assert model.Recipe.query.first().abv == 0
        assert model.Recipe.query.first().srm == 0
        assert model.Recipe.query.first().ibu == 0


class TestRecipeViews(TestModel):

    def test_views(self):
        recipe = model.Recipe()
        for i in range(5):
            model.RecipeView(recipe=recipe)
        model.commit()

        assert len(model.Recipe.query.first().views) == 5

    def test_duplicate_recipe_with_views(self):
        """
        When a recipe is duplicated, its view count should reset.
        """
        recipe = model.Recipe(state="PUBLISHED")
        for i in range(5):
            model.RecipeView(recipe=recipe)
        model.commit()

        model.Recipe.query.first().draft()
        model.commit()

        assert len(model.Recipe.get_by(state="PUBLISHED").views) == 5
        assert len(model.Recipe.get_by(state="DRAFT").views) == 0
