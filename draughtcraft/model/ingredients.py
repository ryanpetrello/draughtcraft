from elixir import (
    Entity, Field, Integer, Float, Unicode,
    UnicodeText, Boolean, Enum, using_options,
    OneToMany
)
from draughtcraft.model.deepcopy    import ShallowCopyMixin
from draughtcraft.lib.units         import UNITS

ORIGINS = [
    'AUSTRALIAN',
    'BELGIAN',
    'CANADIAN',
    'CZECH',
    'FRENCH',
    'GERMAN',
    'JAPANESE',
    'NEW ZEALAND',
    'POLISH',
    'SLOVENIAN',
    'UK',
    'US'
]


class Ingredient(Entity, ShallowCopyMixin):

    using_options(inheritance='multi', polymorphic=True)
    
    uid                 = Field(Unicode(32), unique=True)
    name                = Field(Unicode(256))
    description         = Field(UnicodeText)
    default_unit        = Field(Enum(*UNITS, native_enum=False), default='POUND', nullable=True)

    @property
    def printed_name(self):
        return self.name

    @property
    def printed_origin(self):
        origin = self.origin
        if len(origin) > 2:
            origin = origin.title()
        return origin


class Fermentable(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    TYPES = [
        'MALT',
        'GRAIN',
        'ADJUNCT',
        'EXTRACT',
        'SUGAR'
    ]
    
    type                = Field(Enum(*TYPES, native_enum=False))
    ppg                 = Field(Integer)
    lovibond            = Field(Float)
    origin              = Field(Enum(*ORIGINS, native_enum=False))

    additions           = OneToMany('RecipeAddition', inverse='fermentable')

    @property
    def printed_name(self):
        return '%s (%s)' % (self.name, self.printed_origin)

    @property
    def printed_type(self):
        if self.type is None:
            return 'Grain'
        value = self.type.capitalize()
        if value == 'Malt': value = 'Grain'
        return value

    @property
    def percent_yield(self):
        return round((self.ppg / 46.00) * 100)


class Hop(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    alpha_acid          = Field(Float())
    origin              = Field(Enum(*ORIGINS, native_enum=False))

    additions           = OneToMany('RecipeAddition', inverse='hop')

    @property
    def printed_name(self):
        return '%s (%s)' % (self.name, self.printed_origin)


class Yeast(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    TYPES = [
        'ALE',
        'LAGER',
        'WILD',
        'MEAD',
        'CIDER',
        'WINE'
    ]

    FORMS = [
        'DRY',
        'LIQUID'
    ]

    FLOCCULATION_VALUES = [
        'LOW',
        'LOW/MEDIUM',
        'MEDIUM',
        'MEDIUM/HIGH',
        'HIGH'
    ]

    type                = Field(Enum(*TYPES, native_enum=False))
    form                = Field(Enum(*FORMS, native_enum=False))
    attenuation         = Field(Float())
    flocculation        = Field(Enum(*FLOCCULATION_VALUES, native_enum=False))

    additions           = OneToMany('RecipeAddition', inverse='yeast')


class Extra(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    TYPES = [
        'SPICE',
        'FINING',
        'WATER AGENT',
        'HERB',
        'FLAVOR',
        'OTHER'
    ]

    additions           = OneToMany('RecipeAddition', inverse='extra')

    type                = Field(Enum(*TYPES, native_enum=False))
    liquid              = Field(Boolean)
