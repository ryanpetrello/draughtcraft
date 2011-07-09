from draughtcraft           import model
from datetime               import timedelta


class TestCalculations(object):

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
