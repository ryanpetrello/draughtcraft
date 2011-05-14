from beerparts.lib.units        import UnitConvert, InvalidUnitException
from pytest                     import raises

class TestUnitConversionFromString(object):

    def test_pair_detection(self):
        """
        Coverage for UnitConvert.__pairs__
        """

        # Simple
        pairs = UnitConvert.__pairs__('2lb')
        assert pairs == [(2.0, 'POUND')]

        pairs = UnitConvert.__pairs__('2lb 5oz')
        assert pairs == [(2.0, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb 5oz')
        assert pairs == [(2.5, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb 5.5oz')
        assert pairs == [(2.5, 'POUND'), (5.5, 'OUNCE')]

        # Abbreviation (period)
        pairs = UnitConvert.__pairs__('2lb.')
        assert pairs == [(2.0, 'POUND')]

        pairs = UnitConvert.__pairs__('2lb. 5oz.')
        assert pairs == [(2.0, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb. 5oz.')
        assert pairs == [(2.5, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb. 5.5oz.')
        assert pairs == [(2.5, 'POUND'), (5.5, 'OUNCE')]

        # Missing spacing
        pairs = UnitConvert.__pairs__('2lb5oz.')
        assert pairs == [(2.0, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb5oz.')
        assert pairs == [(2.5, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb5.5oz.')
        assert pairs == [(2.5, 'POUND'), (5.5, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2lb.5oz.')
        assert pairs == [(2.0, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb.5oz.')
        assert pairs == [(2.5, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb.5.5oz.')
        assert pairs == [(2.5, 'POUND'), (5.5, 'OUNCE')]

    def test_coerce_units(self):
        assert UnitConvert.__coerce_units__(['lb']) == ['POUND']
        assert UnitConvert.__coerce_units__(['lbs']) == ['POUND']
        assert UnitConvert.__coerce_units__(['pound']) == ['POUND']
        assert UnitConvert.__coerce_units__(['Pound']) == ['POUND']
        assert UnitConvert.__coerce_units__(['pounds']) == ['POUND']
        assert UnitConvert.__coerce_units__(['Pounds']) == ['POUND']

        assert UnitConvert.__coerce_units__(['oz']) == ['OUNCE']
        assert UnitConvert.__coerce_units__(['ounce']) == ['OUNCE']
        assert UnitConvert.__coerce_units__(['ounces']) == ['OUNCE']
        assert UnitConvert.__coerce_units__(['Ounce']) == ['OUNCE']
        assert UnitConvert.__coerce_units__(['Ounces']) == ['OUNCE']

        assert UnitConvert.__coerce_units__(['g']) == ['GRAM']
        assert UnitConvert.__coerce_units__(['gram']) == ['GRAM']
        assert UnitConvert.__coerce_units__(['Gram']) == ['GRAM']
        assert UnitConvert.__coerce_units__(['grams']) == ['GRAM']
        assert UnitConvert.__coerce_units__(['Grams']) == ['GRAM']

        assert UnitConvert.__coerce_units__(['t']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['ts']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['tsp']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['tspn']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['teaspoon']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['teaspoons']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['Teaspoon']) == ['TEASPOON']
        assert UnitConvert.__coerce_units__(['Teaspoons']) == ['TEASPOON']

        assert UnitConvert.__coerce_units__(['T']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['tbs']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['tbsp']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['tblsp']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['tblspn']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['tablespoon']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['tablespoons']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['Tablespoon']) == ['TABLESPOON']
        assert UnitConvert.__coerce_units__(['Tablespoons']) == ['TABLESPOON']

        assert UnitConvert.__coerce_units__(['G']) == ['GALLON']
        assert UnitConvert.__coerce_units__(['gal']) == ['GALLON']
        assert UnitConvert.__coerce_units__(['Gal']) == ['GALLON']
        assert UnitConvert.__coerce_units__(['gallon']) == ['GALLON']
        assert UnitConvert.__coerce_units__(['Gallon']) == ['GALLON']
        assert UnitConvert.__coerce_units__(['gallons']) == ['GALLON']
        assert UnitConvert.__coerce_units__(['Gallons']) == ['GALLON']
        
        assert UnitConvert.__coerce_units__(['l']) == ['LITER']
        assert UnitConvert.__coerce_units__(['L']) == ['LITER']
        assert UnitConvert.__coerce_units__(['liter']) == ['LITER']
        assert UnitConvert.__coerce_units__(['Liter']) == ['LITER']
        assert UnitConvert.__coerce_units__(['liters']) == ['LITER']
        assert UnitConvert.__coerce_units__(['Liters']) == ['LITER']

        with raises(InvalidUnitException):
            UnitConvert.__coerce_units__(['Invalid'])
            UnitConvert.__coerce_units__([''])

    def test_pound(self):
        amount, unit = UnitConvert.from_str('2lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2Lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2LB')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2 lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2 Lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2 LB')
        assert (amount, unit) == (2, 'POUND')

    def test_pound(self):
        amount, unit = UnitConvert.from_str('2lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2Lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2LB')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2 lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2 Lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2 LB')
        assert (amount, unit) == (2, 'POUND')
