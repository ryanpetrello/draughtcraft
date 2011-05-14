from elixir import (
    Entity, Field, Unicode, Interval, Float, Enum, using_options,
    OneToMany, ManyToOne
)
from draughtcraft.lib.units import UnitConvert, UNITS

class Recipe(Entity):

    name                = Field(Unicode(256))

    additions           = OneToMany('RecipeAddition', inverse='recipe')

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
                percentages[addition] = float(addition.amount) / float(total)

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
    unit                = Field(Enum(*UNITS))
    use                 = Field(Enum(*USES))
    duration            = Field(Interval)

    recipe              = ManyToOne('Recipe', inverse='additions')
    fermentable         = ManyToOne('Fermentable', inverse='additions')
    hop                 = ManyToOne('Hop', inverse='additions')
    yeast               = ManyToOne('Yeast', inverse='additions')

    @property
    def printable_amount(self):
        return UnitConvert.to_str(self.amount, self.unit)

    @property
    def ingredient(self):
        for ingredient in ('fermentable', 'hop', 'yeast'):
            match = getattr(self, ingredient, None)
            if match is not None:
                return match

    def percentage_for(self, step):
        if step not in ('mash', 'boil', 'fermentation'):
            return 0

        additions = getattr(self.recipe, step)
        return self.recipe._percent(additions).get(self, 0)


class HopAddition(RecipeAddition):

    FORMS = [
        'LEAF',
        'PELLET',
        'PLUG'
    ]

    form                = Field(Enum(*FORMS))
    alpha_acid          = Field(Float())

    using_options(inheritance='multi', polymorphic=True)
