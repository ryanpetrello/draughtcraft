from elixir import (
    Entity, Field, Integer, Float, Unicode,
    UnicodeText, Enum, using_options
)

ORIGINS = [
    'AUSTRALIAN',
    'BELGIAN',
    'CANADIAN',
    'CZECH',
    'FRENCH',
    'POLISH',
    'SLOVENIAN',
    'GERMAN',
    'UNITED KINGDOM',
    'UNITED STATES'
]


class Ingredient(Entity):

    using_options(inheritance='multi', polymorphic=True)
    
    name                = Field(Unicode(256), unique=True)
    description         = Field(UnicodeText)


class Fermentable(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    TYPES = [
        'MALT',
        'ADJUNCT',
        'EXTRACT',
        'SUGAR'
    ]
    
    type                = Field(Enum(*TYPES))
    ppg                 = Field(Integer)
    lovibond            = Field(Integer)
    origin              = Field(Enum(*ORIGINS))


class Hop(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    alpha_acid          = Field(Float())
    origin              = Field(Enum(*ORIGINS))


class Yeast(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    TYPES = [
        'ALE',
        'LAGER',
        'WILD'
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

    type                = Field(Enum(*TYPES))
    form                = Field(Enum(*FORMS))
    attenuation         = Field(Float())
    flocculation        = Field(Enum(*FLOCCULATION_VALUES))
    tolerance           = Field(Integer)
