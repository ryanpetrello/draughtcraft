import re

UNITS = [
    'GRAM',
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


class UnitConvert(object):
    """
    Used to convert from strings to units, e.g.,
    from_str("5lb 8oz") == (5.5, 'POUND')

    ...and back again:

    to_str((5.5, 'POUND')) --> "5lb 8oz"
    """

    punctuationRe = re.compile('[^0-9a-zA-z.]')
    unitRe = re.compile('[a-zA-Z]+\.?')
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
        return [float(a) for a in amounts]

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
            OunceMerge
        ]:
            if mergecls.signature == units:
                return mergecls.merge(*pairs)

        return pairs[0]

    @classmethod
    def to_str(cls, amount, unit):
        return (amount, unit)


