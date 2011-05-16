from elixir import (
    Entity, Field, Integer, Float, Unicode,
    UnicodeText, Enum, using_options,
    OneToMany
)
from sqlalchemy import not_

ORIGINS = [
    'AUSTRALIAN',
    'BELGIAN',
    'CANADIAN',
    'CZECH',
    'FRENCH',
    'POLISH',
    'SLOVENIAN',
    'GERMAN',
    'UK',
    'US'
]


class Ingredient(Entity):

    using_options(inheritance='multi', polymorphic=True)
    
    name                = Field(Unicode(256))
    description         = Field(UnicodeText)

    @property
    def printed_name(self):
        return self.name

    @classmethod
    def excluding(cls, *ingredients):
        identifiers = [i.id for i in ingredients]
        return cls.query.filter(not_(cls.id.in_(identifiers))).all()


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

    additions           = OneToMany('RecipeAddition', inverse='fermentable')

    @property
    def printed_name(self):
        origin = self.origin
        if len(origin) > 2:
            origin = origin.title()
        return '%s (%s)' % (self.name, origin)


class Hop(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    alpha_acid          = Field(Float())
    origin              = Field(Enum(*ORIGINS))

    additions           = OneToMany('RecipeAddition', inverse='hop')


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

    additions           = OneToMany('RecipeAddition', inverse='yeast')
