from elixir import (
    Entity, Field, Integer, Float, Unicode,
    UnicodeText, Enum, using_options,
    OneToMany
)
from draughtcraft.model.deepcopy    import ShallowCopyMixin
from draughtcraft.lib.units         import UNITS
from sqlalchemy                     import not_

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
    default_unit        = Field(Enum(*UNITS), default='POUND', nullable=True)

    @property
    def printed_name(self):
        return self.name

    @classmethod
    def excluding(cls, *ingredients):
        identifiers = [i.id for i in ingredients]

        query = cls.query
        if identifiers:
            query = query.filter(not_(cls.id.in_(identifiers)))

        return query.all()


class Fermentable(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    TYPES = [
        'MALT',
        'GRAIN',
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

    @property
    def printed_name(self):
        origin = self.origin
        if len(origin) > 2:
            origin = origin.title()
        return '(%s) %s' % (origin, self.name)


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

    type                = Field(Enum(*TYPES))
    form                = Field(Enum(*FORMS))
    attenuation         = Field(Float())
    flocculation        = Field(Enum(*FLOCCULATION_VALUES))

    additions           = OneToMany('RecipeAddition', inverse='yeast')


class Extra(Ingredient):

    using_options(inheritance='multi', polymorphic=True)

    additions           = OneToMany('RecipeAddition', inverse='extra')
