from draughtcraft import model
from datetime import timedelta

import unittest


class TestCalculations(unittest.TestCase):

    def test_ibu_formula_selection_with_author(self):
        """
        The IBU calculation formula used should be whatever the recipe's
        author has specified.
        """
        user = model.User()
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5,
            author      = user
        )
        model.HopAddition(
            recipe      = recipe,
            hop         = model.Hop(name = 'Cascade'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.HopAddition(
            recipe      = recipe,
            hop         = model.Hop(name = 'Centennial'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=60),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )

        assert user.settings['default_ibu_formula'] == 'tinseth'
        assert recipe.calculations.ibu == recipe.calculations.tinseth

        user.settings['default_ibu_formula'] = 'rager'
        assert recipe.calculations.ibu == recipe.calculations.rager

        user.settings['default_ibu_formula'] = 'daniels'
        assert recipe.calculations.ibu == recipe.calculations.daniels

    def test_ibu_formula_selection_no_author(self):
        """
        If a recipe has no author, it should fall back to Tinseth's formula.
        """
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5
        )
        model.HopAddition(
            recipe      = recipe,
            hop         = model.Hop(name = 'Cascade'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=30),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )
        model.HopAddition(
            recipe      = recipe,
            hop         = model.Hop(name = 'Centennial'),
            amount      = .0625, # 1 oz
            unit        = 'POUND',
            duration    = timedelta(minutes=60),
            alpha_acid  = 5.5,
            form        = 'LEAF',
            use         = 'BOIL'
        )

        assert recipe.calculations.ibu == recipe.calculations.tinseth


class TestCachedCalcuations(unittest.TestCase):

    def test_og_cache(self):
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5,
            _og         = 1.050
        )
        assert recipe.og == 1.050
        with self.assertRaises(AttributeError):
            recipe.og = 1.080
        assert recipe.og == 1.050

    def test_fg_cache(self):
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5,
            _fg         = 1.050
        )
        assert recipe.fg == 1.050
        with self.assertRaises(AttributeError):
            recipe.fg = 1.080
        assert recipe.fg == 1.050

    def test_abv_cache(self):
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5,
            _abv        = 8.0
        )
        assert recipe.abv == 8.0
        with self.assertRaises(AttributeError):
            recipe.abv = 6.0
        assert recipe.abv == 8.0

    def test_srm_cache(self):
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5,
            _srm        = 10
        )
        assert recipe.srm == 10
        with self.assertRaises(AttributeError):
            recipe.srm = 20
        assert recipe.srm == 10

    def test_ibu_cache(self):
        recipe = model.Recipe(
            name        = 'Rocky Mountain River IPA', 
            gallons     = 5,
            _ibu        = 30
        )
        assert recipe.ibu == 30
        with self.assertRaises(AttributeError):
            recipe.ibu = 40
        assert recipe.ibu == 30
