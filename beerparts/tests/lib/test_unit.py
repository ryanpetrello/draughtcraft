from beerparts.lib.units        import (UnitConvert, InvalidUnitException, PoundOunceMerge, 
                                        OunceMerge, PoundExpansion, UNIT_MAP)
from pytest                     import raises


class TestMergeImplementations(object):

    def test_pound_ounce_merge(self):
        assert PoundOunceMerge.merge((5.0, 'POUND'), (8.0, 'OUNCE')) == (5.5, 'POUND')

    def test_ounce_merge(self):
        assert OunceMerge.merge((8.0, 'OUNCE')) == (.5, 'POUND')

class TestExpansionImplemenations(object):

    def test_pound_expansion(self):
        assert PoundExpansion.expand(5.0) == [(5.0, 'POUND')]

        assert PoundExpansion.expand(.0625) == [(0.0, 'POUND'), (1.0, 'OUNCE')]
        assert PoundExpansion.expand(.125) == [(0.0, 'POUND'), (2.0, 'OUNCE')]
        assert PoundExpansion.expand(.1875) == [(0.0, 'POUND'), (3.0, 'OUNCE')]
        assert PoundExpansion.expand(.25) == [(0.0, 'POUND'), (4.0, 'OUNCE')]
        assert PoundExpansion.expand(.3125) == [(0.0, 'POUND'), (5.0, 'OUNCE')]
        assert PoundExpansion.expand(.375) == [(0.0, 'POUND'), (6.0, 'OUNCE')]
        assert PoundExpansion.expand(.4375) == [(0.0, 'POUND'), (7.0, 'OUNCE')]
        assert PoundExpansion.expand(.5) == [(0.0, 'POUND'), (8.0, 'OUNCE')]
        assert PoundExpansion.expand(.5625) == [(0.0, 'POUND'), (9.0, 'OUNCE')]
        assert PoundExpansion.expand(.625) == [(0.0, 'POUND'), (10.0, 'OUNCE')]
        assert PoundExpansion.expand(.6875) == [(0.0, 'POUND'), (11.0, 'OUNCE')]
        assert PoundExpansion.expand(.75) == [(0.0, 'POUND'), (12.0, 'OUNCE')]
        assert PoundExpansion.expand(.8125) == [(0.0, 'POUND'), (13.0, 'OUNCE')]
        assert PoundExpansion.expand(.875) == [(0.0, 'POUND'), (14.0, 'OUNCE')]
        assert PoundExpansion.expand(.9375) == [(0.0, 'POUND'), (15.0, 'OUNCE')]

        assert PoundExpansion.expand(5.0625) == [(5.0, 'POUND'), (1.0, 'OUNCE')]
        assert PoundExpansion.expand(5.125) == [(5.0, 'POUND'), (2.0, 'OUNCE')]
        assert PoundExpansion.expand(5.1875) == [(5.0, 'POUND'), (3.0, 'OUNCE')]
        assert PoundExpansion.expand(5.25) == [(5.0, 'POUND'), (4.0, 'OUNCE')]
        assert PoundExpansion.expand(5.3125) == [(5.0, 'POUND'), (5.0, 'OUNCE')]
        assert PoundExpansion.expand(5.375) == [(5.0, 'POUND'), (6.0, 'OUNCE')]
        assert PoundExpansion.expand(5.4375) == [(5.0, 'POUND'), (7.0, 'OUNCE')]
        assert PoundExpansion.expand(5.5) == [(5.0, 'POUND'), (8.0, 'OUNCE')]
        assert PoundExpansion.expand(5.5625) == [(5.0, 'POUND'), (9.0, 'OUNCE')]
        assert PoundExpansion.expand(5.625) == [(5.0, 'POUND'), (10.0, 'OUNCE')]
        assert PoundExpansion.expand(5.6875) == [(5.0, 'POUND'), (11.0, 'OUNCE')]
        assert PoundExpansion.expand(5.75) == [(5.0, 'POUND'), (12.0, 'OUNCE')]
        assert PoundExpansion.expand(5.8125) == [(5.0, 'POUND'), (13.0, 'OUNCE')]
        assert PoundExpansion.expand(5.875) == [(5.0, 'POUND'), (14.0, 'OUNCE')]
        assert PoundExpansion.expand(5.9375) == [(5.0, 'POUND'), (15.0, 'OUNCE')]

        assert PoundExpansion.expand(5.1713) == [(5.1713, 'POUND')]


class TestUnitConversionFromString(object):

    def test_pair_detection(self):
        """
        Coverage for UnitConvert.__pairs__
        """

        # Simple
        pairs = UnitConvert.__pairs__('2lb')
        assert pairs == [(2.0, 'POUND')]

        pairs = UnitConvert.__pairs__('2Lb')
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

    def test_coerce_amounts(self):
        assert UnitConvert.__coerce_amounts__(['525.75']) == [525.75]

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

    def test_pound_conversion(self):
        amount, unit = UnitConvert.from_str('2lb')
        assert (amount, unit) == (2, 'POUND')

        amount, unit = UnitConvert.from_str('2.5lb')
        assert (amount, unit) == (2.5, 'POUND')

    def test_ounce_conversion(self):
        amount, unit = UnitConvert.from_str('8oz')
        assert (amount, unit) == (.5, 'POUND')

        amount, unit = UnitConvert.from_str('8.5oz')
        assert (amount, unit) == (.53125, 'POUND')

    def test_pound_ounce_conversion(self):
        amount, unit = UnitConvert.from_str('2lb 8oz')
        assert (amount, unit) == (2.5, 'POUND')

        amount, unit = UnitConvert.from_str('2.5lb 8oz')
        assert (amount, unit) == (3, 'POUND')

        amount, unit = UnitConvert.from_str('2.5lb 8.5oz')
        assert (amount, unit) == (3.03125, 'POUND')

    def test_basic_conversion(self):
        for abbr, value in UNIT_MAP.items():
            if value != 'OUNCE':
                assert UnitConvert.from_str('5%s' % abbr) == (5, UNIT_MAP[abbr])


class TestUnitConversionToString(object):

    def test_simple_conversion(self):
        assert UnitConvert.to_str(5, 'POUND') == '5 lb'
        assert UnitConvert.to_str(5, 'OUNCE') == '5 oz'
        assert UnitConvert.to_str(5, 'GRAM') == '5 g'
        assert UnitConvert.to_str(5, 'TEASPOON') == '5 t'
        assert UnitConvert.to_str(5, 'TABLESPOON') == '5 T'
        assert UnitConvert.to_str(5, 'GALLON') == '5 Gal'
        assert UnitConvert.to_str(5, 'LITER') == '5 L'

    def test_simple_conversion_decimal_format(self):
        assert UnitConvert.to_str(5.0, 'POUND') == '5 lb'
        assert UnitConvert.to_str(5.0, 'OUNCE') == '5 oz'
        assert UnitConvert.to_str(5.0, 'GRAM') == '5 g'
        assert UnitConvert.to_str(5.0, 'TEASPOON') == '5 t'
        assert UnitConvert.to_str(5.0, 'TABLESPOON') == '5 T'
        assert UnitConvert.to_str(5.0, 'GALLON') == '5 Gal'
        assert UnitConvert.to_str(5.0, 'LITER') == '5 L'

    def test_decimal_conversion(self):
        assert UnitConvert.to_str(5.1, 'POUND') == '5.1 lb'
        assert UnitConvert.to_str(5.1, 'OUNCE') == '5.1 oz'
        assert UnitConvert.to_str(5.1, 'GRAM') == '5.1 g'
        assert UnitConvert.to_str(5.1, 'TEASPOON') == '5.1 t'
        assert UnitConvert.to_str(5.1, 'TABLESPOON') == '5.1 T'
        assert UnitConvert.to_str(5.1, 'GALLON') == '5.1 Gal'
        assert UnitConvert.to_str(5.1, 'LITER') == '5.1 L'

    def test_pound_ounce_expansion(self):
        assert UnitConvert.to_str(5.25, 'POUND') == '5 lb 4 oz'
        assert UnitConvert.to_str(.25, 'POUND') == '4 oz'
