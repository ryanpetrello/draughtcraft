from elixir import (
    Entity, Field, Unicode, Interval, Float, Enum, using_options,
    OneToMany, ManyToOne
)
from draughtcraft.lib.calculations  import Calculations
from draughtcraft.lib.units         import UnitConvert, UNITS

import math

class Recipe(Entity):

    name                = Field(Unicode(256))

    additions           = OneToMany('RecipeAddition', inverse='recipe')

    @property
    def calculations(self):
        return Calculations(self)

    @property
    def efficiency(self):
        return .75

    @property
    def gallons(self):
        return 5

    def _partition(self, additions):
        """
        Partition a set of recipe additions
        by ingredient type, e.g.,:

        _partition([grain, grain2, hop])
        {'Fermentable': [grain, grain2], 'Hop': [hop]}
        """
        p = {}
        for a in additions:
            p.setdefault(a.ingredient.__class__, []).append(a)
        return p

    def _percent(self, partitions):
        """
        Calculate percentage of additions by amount
        within a set of recipe partitions.
        e.g.,

        _percent({'Fermentable': [grain, grain2], 'Hop': [hop]})
        {grain : .75, grain2 : .25, hop : 1}
        """

        percentages = {}
        for type, additions in partitions.items():
            total = sum([addition.amount for addition in additions])
            for addition in additions:
                if total:
                    percentages[addition] = float(addition.amount) / float(total)
                else:
                    percentages[addition] = 0

        return percentages

    @property
    def mash(self):
        return self._partition([a for a in self.additions if a.use == 'MASH'])

    @property
    def boil(self):
        return self._partition([a for a in self.additions if a.use in (
            'FIRST WORT',
            'BOIL',
            'POST-BOIL',
            'FLAME OUT'
        )])

    @property
    def fermentation(self):
        return self._partition([a for a in self.additions if a.use in (
            'PRIMARY',
            'SECONDARY'
        )])

    def contains(self, ingredient, step):
        if step not in ('mash', 'boil', 'fermentation'):
            return False

        additions = getattr(self, step)
        for a in sum(additions.values(), []):
            if a.ingredient == ingredient:
                return True

        return False


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

    using_options(inheritance='multi', polymorphic=True)

    amount              = Field(Float)
    unit                = Field(Enum(*UNITS), nullable=True)
    use                 = Field(Enum(*USES))
    duration            = Field(Interval)

    recipe              = ManyToOne('Recipe', inverse='additions')
    fermentable         = ManyToOne('Fermentable', inverse='additions')
    hop                 = ManyToOne('Hop', inverse='additions')
    yeast               = ManyToOne('Yeast', inverse='additions')
    extra               = ManyToOne('Extra', inverse='extra')

    @property
    def printable_amount(self):
        return UnitConvert.to_str(self.amount, self.unit)

    @property
    def ingredient(self):
        for ingredient in ('fermentable', 'hop', 'yeast', 'extra'):
            match = getattr(self, ingredient, None)
            if match is not None:
                return match

    @property
    def minutes(self):
        if self.duration is None:
            return 0
        return self.duration.seconds / 60

    @property
    def step(self):
        return ({
            'MASH'          : 'mash',
            'FIRST WORT'    : 'boil',
            'BOIL'          : 'boil',
            'POST-BOIL'     : 'boil',
            'FLAME OUT'     : 'boil',
            'PRIMARY'       : 'fermentation',
            'SECONDARY'     : 'fermentation'
        })[self.use]

    @property
    def percentage(self):
        additions = getattr(self.recipe, self.step)
        return self.recipe._percent(additions).get(self, 0)


class HopAddition(RecipeAddition):

    FORMS = [
        'LEAF',
        'PELLET',
        'PLUG'
    ]

    form                = Field(Enum(*FORMS), default='LEAF')
    alpha_acid          = Field(Float())

    using_options(inheritance='multi', polymorphic=True)

    @property
    def printable_amount(self):
        unit = self.unit
        if self.amount == 0:
            unit = 'OUNCE'
        return UnitConvert.to_str(self.amount, unit)
