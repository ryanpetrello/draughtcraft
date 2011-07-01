from elixir import (
    Entity, Field, Unicode, UnicodeText, Integer, Interval, Float, Enum,
    using_options, OneToMany, ManyToOne, entities
)
from draughtcraft.lib.calculations  import Calculations
from draughtcraft.lib.units         import UnitConvert

class Recipe(Entity):

    TYPES = (
        'MASH',
        'EXTRACT',
        'EXTRACTSTEEP',
        'MINIMASH'
    )

    type                = Field(Enum(*TYPES), default='MASH')
    name                = Field(Unicode(256))
    gallons             = Field(Float, default=5)
    notes               = Field(UnicodeText)

    additions           = OneToMany('RecipeAddition', inverse='recipe')
    fermentation_steps  = OneToMany('FermentationStep', inverse='recipe')
    slugs               = OneToMany('RecipeSlug', inverse='recipe')
    style               = ManyToOne('Style', inverse='recipes')
    author              = ManyToOne('User', inverse='recipes')

    def __init__(self, **kwargs):
        super(Recipe, self).__init__(**kwargs)
        if kwargs.get('name'):
            self.slugs.append(
                entities.RecipeSlug(name=kwargs['name'])
            )

    @property
    def calculations(self):
        return Calculations(self)

    @property
    def efficiency(self):
        return .75

    @property
    def boil_minutes(self):
        return 60

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
        return self._partition([a for a in self.additions if a.step == 'mash'])

    @property
    def boil(self):
        return self._partition([a for a in self.additions if a.step == 'boil'])

    @property
    def fermentation(self):
        return self._partition([a for a in self.additions if a.step == 'fermentation'])

    def contains(self, ingredient, step):
        if step not in ('mash', 'boil', 'fermentation'):
            return False

        additions = getattr(self, step)
        for a in sum(additions.values(), []):
            if a.ingredient == ingredient:
                return True

        return False

    @property
    def next_fermentation_step(self):
        """
        The next available fermentation step for a recipe.
        e.g., if temperature/length is already defined for "PRIMARY" a
        fermentation period, returns "SECONDARY".  If "SECONDARY" is already
        defined, returns "TERTIARY".

        Always returns one of `model.FermentationStep.STEPS`.
        """

        total = len(self.fermentation_steps)

        return {
            1   : 'SECONDARY',
            2   : 'TERTIARY'
        }.get(total, None)

    def url(self, public=True):
        """
        The URL for a recipe.
        """
        return '/recipes/%s/%s/%s' % (
            self.id,
            self.slugs[0].slug,
            '' if public else 'builder'
        )

    @property
    def printable_type(self):
        return {
            'MASH'          : 'All Grain',
            'EXTRACT'       : 'Extract',
            'EXTRACTSTEEP'  : 'Extract with Steeped Grains',
            'MINIMASH'      : 'Extract with Mini-Mash'
        }[self.type]


class RecipeAddition(Entity):

    USES = (
        'MASH',
        'FIRST WORT',
        'BOIL',
        'POST-BOIL',
        'FLAME OUT',
        'PRIMARY',
        'SECONDARY',
        'TERTIARY'
    )

    using_options(inheritance='multi', polymorphic=True)

    amount              = Field(Float)

    #
    # At the database level, only certain units are actually stored.
    # We do this for the sake of uniformity (to make calculations easier).
    #
    unit                = Field(Enum(*[
                                'POUND',
                                'TEASPOON',
                                'TABLESPOON',
                                'GALLON'
                            ]), nullable=True)

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

    FORMS = (
        'LEAF',
        'PELLET',
        'PLUG'
    )

    form                = Field(Enum(*FORMS), default='LEAF')
    alpha_acid          = Field(Float())

    using_options(inheritance='multi', polymorphic=True)

    @property
    def printable_amount(self):
        unit = self.unit
        if self.amount == 0:
            unit = 'OUNCE'
        return UnitConvert.to_str(self.amount, unit)


class FermentationStep(Entity):

    STEPS = (
        'PRIMARY',
        'SECONDARY',
        'TERTIARY'
    )

    step            = Field(Enum(*STEPS))
    days            = Field(Integer)
    fahrenheit      = Field(Float)

    recipe          = ManyToOne('Recipe', inverse='fermentation_steps')
