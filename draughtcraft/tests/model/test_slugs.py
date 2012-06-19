from draughtcraft import model

import unittest


class TestSlugGeneration(unittest.TestCase):

    def test_custom_slug(self):
        slug = model.RecipeSlug(
            name = 'American Ale',
            slug = 'custom'
        )
        assert slug.slug == 'custom'

    def test_slug_generation(self): 
        slug = model.RecipeSlug(name='Beer')
        assert slug.slug == 'beer'

        slug = model.RecipeSlug(name='American Ale')
        assert slug.slug == 'american-ale'

        slug = model.RecipeSlug(name="Ryan's American Ale")
        assert slug.slug == 'ryans-american-ale'

        slug = model.RecipeSlug(name='Fancy Wit-Bier')
        assert slug.slug == 'fancy-wit-bier'

        slug = model.RecipeSlug(name='Spaced Out  IPA')
        assert slug.slug == 'spaced-out-ipa'

        slug = model.RecipeSlug(name='Holy Moly! Imperial Stout')
        assert slug.slug == 'holy-moly-imperial-stout'

        slug = model.RecipeSlug(name='$$$')
        assert slug.slug == 'custom-recipe'
