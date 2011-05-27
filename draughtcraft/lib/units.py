from formencode import validators, Invalid
import re

UNITS = [
    'GRAM',
    'KILOGRAM',
    'OUNCE',
    'POUND',
    'TEASPOON',
    'TABLESPOON',
    'GALLON',
    'LITER'
]

UNIT_MAP = {
    'lb'            : 'POUND',
    'Lb'            : 'POUND',
    'LB'            : 'POUND',
    'oz'            : 'OUNCE',
    'Oz'            : 'OUNCE',
    'OZ'            : 'OUNCE',
    'g'             : 'GRAM',
    'kg'            : 'KILOGRAM',
    't'             : 'TEASPOON',
    'ts'            : 'TEASPOON',
    'tsp'           : 'TEASPOON',
    'Tsp'           : 'TEASPOON',
    'tspn'          : 'TEASPOON',
    'tbs'           : 'TABLESPOON',
    'tbsp'          : 'TABLESPOON',
    'tblsp'         : 'TABLESPOON',
    'tblspn'        : 'TABLESPOON',
    'Tbsp'          : 'TABLESPOON',
    'T'             : 'TABLESPOON',
    'G'             : 'GALLON',
    'gal'           : 'GALLON',
    'Gal'           : 'GALLON',
    'l'             : 'LITER',
    'L'             : 'LITER'
}


class UnitException(Exception):
    pass


class InvalidUnitException(UnitException):
    pass


class InvalidUnitParseException(UnitException):
    pass


class PoundOunceMerge(object):

    signature = ["POUND", "OUNCE"]

    @classmethod
    def merge(cls, pounds, ounces):
        return (pounds[0] + (ounces[0] / 16), 'POUND')


class OunceMerge(object):

    signature = ["OUNCE"]

    @classmethod
    def merge(cls, ounces):
        return (ounces[0] / 16, 'POUND')


class GramMerge(object):

    signature = ["GRAM"]

    @classmethod
    def merge(cls, grams):
        return (grams[0] / 453.59237, "POUND")


class KilogramMerge(object):

    signature = ["KILOGRAM"]

    @classmethod
    def merge(cls, kilograms):
        return (kilograms[0] / .45359237, "POUND")


class PoundExpansion(object):

    signature = "POUND"

    @classmethod
    def expand(cls, pounds):
        """
        Attempt to expand POUND units into whole POUND, OUNCE units, e.g.,

        5.5 lb == 5 lb, 8 oz

        If the unit is less than a pound, just use ounce increments.
        """

        #
        # If we already have an integer, just return it
        #
        if int(pounds) == pounds:
            return [(pounds, "POUND")]

        #
        # If we have less than a pound,
        # just use ounces.
        #
        if pounds < 1:
            return [(pounds * 16, "OUNCE")]

        #
        # There's 16 oz in a lb.
        # Multiply the weight in pounds by individual
        # ounce increments (e.g., 1, 2, 3...).
        #
        # If the result is roughly an integer,
        # we can split into lbs, oz.
        #
        for i in range(16):

            # We're only interested in the fractional part.
            decimal = pounds - int(pounds)
            if (decimal * 16) == i+1:
                return [(int(pounds), "POUND"), (i+1, "OUNCE")]

        #
        # If we find no round fractions,
        # just return a pounds in decimal format.
        #
        return [(pounds, "POUND")]


class UnitConvert(object):
    """
    Used to convert from strings to units, e.g.,
    from_str("5lb 8oz") == (5.5, 'POUND')

    ...and back again:

    to_str((5.5, 'POUND')) --> "5lb 8oz"
    """

    punctuationRe = re.compile('[^0-9a-zA-z.\s]')
    unitRe = re.compile('[a-zA-Z]+( \.)?')
    amountRe = re.compile('[0-9]+')

    @classmethod
    def __pairs__(cls, val):
        """
        Convert a unit string into a list of pairs
        '2.5lb. 6oz' --> [(2.5, 'lb'), (6, 'oz')]

        Input should already be stripped of any [^0-9a-zA-Z.] characters.
        """

        # Find all unit amounts
        amounts = filter(None, cls.unitRe.split(val))
        amounts = filter(lambda x: x != '.', amounts)

        # Build a regex that matches the amounts
        partsRe = '(%s)' % '|'.join(amounts).replace('.', '\.') 

        #
        # Split on the regex, and filter out the amounts,
        # leaving only the remainder.
        #
        parts = re.compile(partsRe).split(val)
        units = filter(None, parts)
        for a in amounts:
            units = [u for u in units if u != a]

        # Coerce values into a more usable format
        amounts = cls.__coerce_amounts__(amounts)
        units = cls.__coerce_units__(units)

        return zip(amounts, units)

    @classmethod
    def __coerce_amounts__(cls, amounts):
        # Cast the amounts to float
        return [float(a.replace('. ', '')) for a in amounts]

    @classmethod
    def __coerce_units__(cls, units):
        # Filter all punctuation from the units
        units = [re.compile('[^a-zA-Z]').sub('', u) for u in units]

        # Attempt to standardize units
        def unitize(unit):
            coerced = None

            # Look for exact matches
            if unit.upper() in UNITS:
                coerced = unit.upper()

            # Look for alias matches
            if unit in UNIT_MAP:
                coerced = UNIT_MAP[unit]

            # Look for simple matches on plurality
            if unit[-1] == 's' and unit[:-1].upper() in UNITS:
                coerced = unit[:-1].upper()

            # Look for simple alias matches on plurality
            if unit[-1] == 's' and unit[:-1] in UNIT_MAP:
                coerced = UNIT_MAP[unit[:-1]]

            if coerced not in UNITS:
                raise InvalidUnitException('Invalid unit type %s' % unit)

            return coerced

        units = [unitize(u) for u in units]

        return units

    @classmethod
    def from_str(cls, val):
        stripped = cls.punctuationRe.sub('', val)

        #
        # First attempt to interpret a simple int/float
        # value and return it.  If this fails, continue on
        # to normal "<amount> <unit>" parsing.
        #
        try:
            return validators.Number.to_python(stripped), None
        except Invalid: pass

        #
        # Split into pairs of (amount, unit), e.g.,
        # [(5.0, 'POUND'), (8.0, 'OUNCE')]
        #
        pairs = cls.__pairs__(stripped)

        #
        # Now that we have a list of potential
        # unit/amonut pairs, attempt to combine
        # them into a single unit that makes sense, e.g.,
        #
        # [(5.0, 'POUND'), (8.0, 'OUNCE')] == (5.5, 'POUND')
        #
        units = [p[1] for p in pairs]
        
        for mergecls in [
            PoundOunceMerge,
            OunceMerge,
            GramMerge,
            KilogramMerge
        ]:
            if mergecls.signature == units:
                return mergecls.merge(*pairs)

        return pairs[0]

    @classmethod
    def __str_abbr__(cls, unit):
        """
        Abbreviate standard units, e.g.,
        "POUND" -> "lb"
        """

        unit = str(unit)
        _map = {
            'GRAM'          : 'g',
            'OUNCE'         : 'oz',
            'POUND'         : 'lb',
            'TEASPOON'      : 't',
            'TABLESPOON'    : 'T',
            'GALLON'        : 'Gal',
            'LITER'         : 'L'
        }
        return _map[unit]

    @classmethod
    def __str_amount__(cls, amount):
        """
        Format amounts for readability, e.g.,
        5.0 -> 5
        """
        if amount == int(amount):
            amount = int(amount)
        return str(amount)

    @classmethod
    def to_str(cls, amount, unit):

        #
        # If there's no unit, just
        # return the amount
        #
        if unit is None:
            if type(amount) is float and int(amount) == amount:
                amount = int(amount)
            return str(amount)

        pairs = [(amount, unit)]

        for expandcls in [
            PoundExpansion
        ]:
            if expandcls.signature == unit:
                pairs = expandcls.expand(amount)

        result = ' '.join(['%s %s' % (cls.__str_amount__(amount), cls.__str_abbr__(unit)) for amount, unit in pairs if amount])

        #
        # If result is an empty string,
        # we filtered out all of the "zero"
        # ingredients, leaving nothing.
        #
        # This can happen in circumstances like
        # (0, 'POUND').  This scenario is
        # special cased.
        #
        if result == '':
            return '0 %s' % cls.__str_abbr__(unit)

        return result
