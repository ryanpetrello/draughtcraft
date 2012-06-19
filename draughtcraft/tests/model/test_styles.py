from draughtcraft import model

import unittest


# Stubs
class FakeCalculations(object): pass
class FakeRecipe(object):

    def __init__(self, **kw):
        self.calculations = FakeCalculations()
        for k,v in kw.items():
            setattr(self.calculations, k, v)


class TestStyleDefined(unittest.TestCase):

    def test_og(self): 
        style = model.Style(
            min_og = 1.050,
            max_og = 1.060
        )
        assert style.defined('og') == True
        style = model.Style(
            max_og = 1.060
        )
        assert style.defined('og') == False
        style = model.Style(
            min_og = 1.050
        )
        assert style.defined('og') == False

    def test_fg(self): 
        style = model.Style(
            min_fg = 1.050,
            max_fg = 1.060
        )
        assert style.defined('fg') == True
        style = model.Style(
            max_fg = 1.060
        )
        assert style.defined('fg') == False
        style = model.Style(
            min_fg = 1.050
        )
        assert style.defined('fg') == False

    def test_ibu(self): 
        style = model.Style(
            min_ibu = 1.050,
            max_ibu = 1.060
        )
        assert style.defined('ibu') == True
        style = model.Style(
            max_ibu = 1.060
        )
        assert style.defined('ibu') == False
        style = model.Style(
            min_ibu = 1.050
        )
        assert style.defined('ibu') == False

    def test_srm(self): 
        style = model.Style(
            min_srm = 1.050,
            max_srm = 1.060
        )
        assert style.defined('srm') == True
        style = model.Style(
            max_srm = 1.060
        )
        assert style.defined('srm') == False
        style = model.Style(
            min_srm = 1.050
        )
        assert style.defined('srm') == False

    def test_abv(self): 
        style = model.Style(
            min_abv = 1.050,
            max_abv = 1.060
        )
        assert style.defined('abv') == True
        style = model.Style(
            max_abv = 1.060
        )
        assert style.defined('abv') == False
        style = model.Style(
            min_abv = 1.050
        )
        assert style.defined('abv') == False

    def test_invalid_statistic(self):
        style = model.Style(
            min_og = 1.050,
            max_og = 1.060
        )
        with self.assertRaises(model.InvalidStatistic):
            assert style.defined('invalid')

class TestStyleMatches(unittest.TestCase):

    def test_og(self):
        recipe = FakeRecipe(**{
            'og':   1.050
        })
        style = model.Style(
            min_og = 1.050,
            max_og = 1.060
        )
        assert style.matches(recipe, 'og')

        recipe.calculations.og = 1.051
        assert style.matches(recipe, 'og')
        recipe.calculations.og = 1.060
        assert style.matches(recipe, 'og')
        recipe.calculations.og = 1.061
        assert style.matches(recipe, 'og') is False

    def test_fg(self):
        recipe = FakeRecipe(**{
            'fg':   1.050
        })
        style = model.Style(
            min_fg = 1.050,
            max_fg = 1.060
        )
        assert style.matches(recipe, 'fg')

        recipe.calculations.fg = 1.051
        assert style.matches(recipe, 'fg')
        recipe.calculations.fg = 1.060
        assert style.matches(recipe, 'fg')
        recipe.calculations.fg = 1.061
        assert style.matches(recipe, 'fg') is False

    def test_abv(self):
        recipe = FakeRecipe(**{
            'abv':   1.050
        })
        style = model.Style(
            min_abv = 1.050,
            max_abv = 1.060
        )
        assert style.matches(recipe, 'abv')

        recipe.calculations.abv = 1.051
        assert style.matches(recipe, 'abv')
        recipe.calculations.abv = 1.060
        assert style.matches(recipe, 'abv')
        recipe.calculations.abv = 1.061
        assert style.matches(recipe, 'abv') is False

    def test_srm(self):
        recipe = FakeRecipe(**{
            'srm':   1.050
        })
        style = model.Style(
            min_srm = 1.050,
            max_srm = 1.060
        )
        assert style.matches(recipe, 'srm')

        recipe.calculations.srm = 1.051
        assert style.matches(recipe, 'srm')
        recipe.calculations.srm = 1.060
        assert style.matches(recipe, 'srm')
        recipe.calculations.srm = 1.061
        assert style.matches(recipe, 'srm') is False

    def test_ibu(self):
        recipe = FakeRecipe(**{
            'ibu':   1.050
        })
        style = model.Style(
            min_ibu = 1.050,
            max_ibu = 1.060
        )
        assert style.matches(recipe, 'ibu')

        recipe.calculations.ibu = 1.051
        assert style.matches(recipe, 'ibu')
        recipe.calculations.ibu = 1.060
        assert style.matches(recipe, 'ibu')
        recipe.calculations.ibu = 1.061
        assert style.matches(recipe, 'ibu') is False

    def test_undefined(self):
        recipe = FakeRecipe(**{
            'ibu':   1.050
        })

        style = model.Style(
            min_ibu = 1.050
        )
        assert style.matches(recipe, 'ibu') is False

        style = model.Style(
            max_ibu = 1.050
        )
        assert style.matches(recipe, 'ibu') is False

    def test_invalid(self):
        recipe = FakeRecipe(**{
            'og':   1.050
        })
        style = model.Style(
            min_og = 1.050,
            max_og = 1.060
        )
        with self.assertRaises(model.InvalidStatistic):
            assert style.matches(recipe, 'invalid')
