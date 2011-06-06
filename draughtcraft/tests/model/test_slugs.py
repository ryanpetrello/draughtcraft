from draughtcraft       import model
import pytest


class TestSlugGeneration(object):

    def test_custom_slug(self):
        slug = model.RecipeSlug(
            name = 'American Ale',
            slug = 'custom'
        )
        assert slug.slug == 'custom'

    def test_slug_generation(self): 
        slug = model.RecipeSlug('Beer')
        assert slug.slug == 'beer'

        slug = model.RecipeSlug('American Ale')
        assert slug.slug == 'american-ale'

        slug = model.RecipeSlug("Ryan's American Ale")
        assert slug.slug == 'ryans-american-ale'

        slug = model.RecipeSlug('Fancy Wit-Bier')
        assert slug.slug == 'fancy-wit-bier'

        slug = model.RecipeSlug('Spaced Out  IPA')
        assert slug.slug == 'spaced-out-ipa'

        slug = model.RecipeSlug('Holy Moly! Imperial Stout')
        assert slug.slug == 'holy-moly-imperial-stout'

        slug = model.RecipeSlug('$$$')
        assert slug.slug == 'custom-recipe'

    def test_empty_name(self):
        with pytest.raises(AssertionError):
            model.RecipeSlug('')
