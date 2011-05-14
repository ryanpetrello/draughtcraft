UNITS = [
    'GRAM',
    'OUNCE',
    'POUND',
    'TEASPOON',
    'TABLESPOON',
    'GALLON',
    'LITER'
]

class UnitConvert(object):

    @classmethod
    def from_str(self, str):
        return str

    @classmethod
    def to_str(self, amount, unit):
        return (amount, unit)
