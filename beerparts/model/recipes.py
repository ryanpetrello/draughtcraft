from elixir import (
    Entity, Field, Unicode, Interval, Float, Enum, using_options,
    OneToMany, ManyToOne
)
from beerparts.lib.units import UNITS

class Recipe(Entity):

    name                = Field(Unicode(256))

    additions           = OneToMany('RecipeAddition', inverse='recipe')


class RecipeAddition(Entity):

    USES = [
        'MASH',
        'FIRST WORT',
        'BOIL',
        'POST-BOIL',
        'FLAME OUT',
        'PRIMARY',
        'SECONDARY'
    ]

    amount              = Field(Float)
    unit                = Field(Enum(*UNITS))
    use                 = Field(Enum(*USES))

    using_options(inheritance='multi', polymorphic=True)

    recipe              = ManyToOne('Recipe', inverse='additions')


class TimedAddition(RecipeAddition):

    duration            = Field(Interval)

class HopAddition(TimedAddition):


    TYPES = [
        'LEAF',
        'PELLET',
        'PLUG'
    ]

    form                = Field(Enum(*TYPES))
    alpha_acid          = Field(Float())

    using_options(inheritance='multi', polymorphic=True)
