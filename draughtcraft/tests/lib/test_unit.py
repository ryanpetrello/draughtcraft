from draughtcraft.lib.units         import (UnitConvert, InvalidUnitException, PoundOunceMerge, 
                                            OunceMerge, GramMerge, KilogramMerge, PoundExpansion,
                                            to_us, to_metric, to_kg, to_l, UNIT_MAP)
from pytest                         import raises

import unittest


class TestMergeImplementations(unittest.TestCase):

    def test_pound_ounce_merge(self):
        assert PoundOunceMerge.merge((5.0, 'POUND'), (8.0, 'OUNCE')) == (5.5, 'POUND')

    def test_ounce_merge(self):
        assert OunceMerge.merge((8.0, 'OUNCE')) == (.5, 'POUND')

    def test_gram_merge(self):
        assert GramMerge.merge((453.59237, 'GRAM')) == (1, 'POUND')

    def test_kilogram_merge(self):
        assert KilogramMerge.merge((0.45359237, 'KILOGRAM')) == (1, 'POUND')

class TestExpansionImplementations(unittest.TestCase):

    def test_pound_expansion(self):
        assert PoundExpansion.expand(5.0) == [(5.0, 'POUND')]

        assert PoundExpansion.expand(.0625) == [(1.0, 'OUNCE')]
        assert PoundExpansion.expand(.125) == [(2.0, 'OUNCE')]
        assert PoundExpansion.expand(.1875) == [(3.0, 'OUNCE')]
        assert PoundExpansion.expand(.25) == [(4.0, 'OUNCE')]
        assert PoundExpansion.expand(.3125) == [(5.0, 'OUNCE')]
        assert PoundExpansion.expand(.375) == [(6.0, 'OUNCE')]
        assert PoundExpansion.expand(.4375) == [(7.0, 'OUNCE')]
        assert PoundExpansion.expand(.5) == [(8.0, 'OUNCE')]
        assert PoundExpansion.expand(.5625) == [(9.0, 'OUNCE')]
        assert PoundExpansion.expand(.625) == [(10.0, 'OUNCE')]
        assert PoundExpansion.expand(.6875) == [(11.0, 'OUNCE')]
        assert PoundExpansion.expand(.75) == [(12.0, 'OUNCE')]
        assert PoundExpansion.expand(.8125) == [(13.0, 'OUNCE')]
        assert PoundExpansion.expand(.875) == [(14.0, 'OUNCE')]
        assert PoundExpansion.expand(.9375) == [(15.0, 'OUNCE')]

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


class TestUnitConversionFromString(unittest.TestCase):

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
        pairs = UnitConvert.__pairs__('2lb5oz')
        assert pairs == [(2.0, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb5oz')
        assert pairs == [(2.5, 'POUND'), (5.0, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb5.5oz')
        assert pairs == [(2.5, 'POUND'), (5.5, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2lb.5oz')
        assert pairs == [(2.0, 'POUND'), (.5, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb.5oz')
        assert pairs == [(2.5, 'POUND'), (.5, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2.5lb5.5oz')
        assert pairs == [(2.5, 'POUND'), (5.5, 'OUNCE')]

        pairs = UnitConvert.__pairs__('2lb.5oz.')
        assert pairs == [(2.0, 'POUND'), (.5, 'OUNCE')]

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

        assert UnitConvert.__coerce_units__(['kg']) == ['KILOGRAM']
        assert UnitConvert.__coerce_units__(['kilogram']) == ['KILOGRAM']
        assert UnitConvert.__coerce_units__(['Kilogram']) == ['KILOGRAM']
        assert UnitConvert.__coerce_units__(['kilograms']) == ['KILOGRAM']
        assert UnitConvert.__coerce_units__(['Kilograms']) == ['KILOGRAM']

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
            if value not in ('OUNCE', 'GRAM', 'KILOGRAM'):
                assert UnitConvert.from_str('5%s' % abbr) == (5, UNIT_MAP[abbr])

    def test_ounce_conversion(self):
        assert UnitConvert.from_str('8oz') == (.5, 'POUND')

    def test_gram_conversion(self):
        assert UnitConvert.from_str('453.59237g') == (1, 'POUND')

    def test_kilogram_conversion(self):
        assert UnitConvert.from_str('.45359237kg') == (1, 'POUND')

    def test_unitless_conversion(self):
        amount, unit = UnitConvert.from_str('5')
        assert (amount, unit) == (5, None)

        amount, unit = UnitConvert.from_str('5.25')
        assert (amount, unit) == (5.25, None)


class TestUnitConversionToString(unittest.TestCase):

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

    def test_zero_amount(self):
        assert UnitConvert.to_str(0, 'POUND') == '0 lb'

    def test_unitless_amount(self):
        assert UnitConvert.to_str(5, None) == '5'
        assert UnitConvert.to_str(5.0, None) == '5'
        assert UnitConvert.to_str(5.25, None) == '5.25'


class TestConversionInteroperability(unittest.TestCase):

    def test_opposites(self):
        original = '5 lb 4 oz'
        units = UnitConvert.from_str(original)
        assert original == UnitConvert.to_str(*units)

        original = (5.25, 'POUND')
        string = UnitConvert.to_str(*original)
        assert original == UnitConvert.from_str(string)


class TestUsConversion(unittest.TestCase):

    def test_kg_to_pound(self):
        """Convert kg to pounds"""
        assert to_us(*(5, 'KILOGRAM')) == (11.0231131, 'POUND')

    def test_gram_to_ounce(self):
        """Convert g to oz"""
        assert to_us(*(50, 'GRAM')) == (1.7636980949999999, 'OUNCE')

    def test_liter_to_gallon(self):
        """Convert liters to gallons"""
        assert to_us(*(20, 'LITER')) == (5.2834410399999996, 'GALLON')

    def test_passthrough(self):
        assert to_us(*(5, 'TSP')) == (5, 'TSP')


class TestMetricConversion(unittest.TestCase):

    def test_pound_to_kg(self):
        """Convert pounds to kg"""
        assert to_metric(*(5, 'POUND')) == (2.2679618500000003, 'KILOGRAM')

    def test_pound_to_g(self):
        """If the pound -> kg conversion is < 1kg, use grams instead"""
        assert to_metric(*(1, 'POUND')) == (453.59237000000002, 'GRAM')

    def test_ounce_to_gram(self):
        """Convert oz to g"""
        assert to_metric(*(1, 'OUNCE')) == (28.3495231, 'GRAM')

    def test_gallon_to_liter(self):
        """Convert gallons to liters"""
        assert to_metric(*(10, 'GALLON')) == (37.854117799999997, 'LITER')

    def test_passthrough(self):
        assert to_metric(*(5, 'TSP')) == (5, 'TSP')

	def test_ounces_to_kg(self):
		assert to_kg(*(16, 'OUNCE')) == 2.2679618500000003

	def test_pound_to_kg(self):
		assert to_kg(*(5, 'POUND')) == 2.2679618500000003

	def test_gram_to_kg(self):
		assert to_kg(*(5, 'GRAM')) == 0.005

	def test_kg_to_kg(self):
		assert to_kg(*(5, 'KILOGRAM')) == 5

    def test_tsp_to_l(self):
        assert to_l(*(5, 'TEASPOON')) == 0.02464460795

    def test_tbsp_to_l(self):
        assert to_l(*(5, 'TABLESPOON')) == 0.073933823999999995

    def test_gallon_to_l(self):
        assert to_l(*(10, 'GALLON')) == 37.854117799999997

    def test_l_to_l(self):
        assert to_l(*(10, 'LITER')) == 10
