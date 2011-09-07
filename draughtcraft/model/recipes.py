from elixir import (
    Entity, Field, Unicode, UnicodeText, Integer, Interval, Float, Enum,
    DateTime, using_options, OneToMany, ManyToOne, OneToOne, entities
)
from draughtcraft.lib.calculations  import Calculations
from draughtcraft.lib.units         import UnitConvert, InvalidUnitException
from draughtcraft.model.deepcopy    import DeepCopyMixin, ShallowCopyMixin
from datetime                       import datetime
from copy                           import deepcopy
from sys                            import maxint


class Recipe(Entity, DeepCopyMixin, ShallowCopyMixin):

    TYPES = (
        'MASH',
        'EXTRACT',
        'EXTRACTSTEEP',
        'MINIMASH'
    )

    MASH_METHODS = {
        'SINGLESTEP',
        'TEMPERATURE',
        'DECOCTION',
        'MULTISTEP'
    }

    STATES = (
        'DRAFT',
        'PUBLISHED'
    )

    type                = Field(Enum(*TYPES), default='MASH', index=True)
    name                = Field(Unicode(256), index=True)
    gallons             = Field(Float, default=5)
    boil_minutes        = Field(Integer, default=60)
    notes               = Field(UnicodeText)
    creation_date       = Field(DateTime, default=datetime.utcnow)
    last_updated        = Field(DateTime, default=datetime.utcnow, index=True)

    mash_method         = Field(Enum(*MASH_METHODS), default='SINGLESTEP')
    mash_instructions   = Field(UnicodeText) 

    state               = Field(Enum(*STATES), default='DRAFT')
    current_draft       = ManyToOne('Recipe', inverse='published_version')
    published_version   = OneToOne('Recipe', inverse='current_draft', order_by='creation_date')

    copied_from         = ManyToOne('Recipe', inverse='copies')
    copies              = OneToMany('Recipe', inverse='copied_from', order_by='creation_date')

    views               = OneToMany('RecipeView', inverse='recipe', cascade='all, delete-orphan')
    additions           = OneToMany('RecipeAddition', inverse='recipe', cascade='all, delete-orphan')
    fermentation_steps  = OneToMany('FermentationStep', inverse='recipe', cascade='all, delete-orphan')
    slugs               = OneToMany('RecipeSlug', inverse='recipe', order_by='id', cascade='all, delete-orphan')
    style               = ManyToOne('Style', inverse='recipes')
    author              = ManyToOne('User', inverse='recipes')

    __ignored_properties__ = (
        'current_draft',
        'published_version',
        'copies',
        'copied_from',
        'views',
        'creation_date',
        'state'
    )

    def __init__(self, **kwargs):
        super(Recipe, self).__init__(**kwargs)
        if kwargs.get('name') and not kwargs.get('slugs'):
            self.slugs.append(
                entities.RecipeSlug(name=kwargs['name'])
            )

    def duplicate(self, overrides={}):
        """
        Used to duplicate a recipe.

        An optional hash of `overrides` can be specified to override the
        default copied values, e.g.,

        dupe = user.recipes[0].duplicate({'author': otheruser})
        assert dupe.author == otheruser
        """
        # Make a deep copy of the instance
        copy = deepcopy(self)

        # For each override...
        for k,v in overrides.items():

            # If the key is already defined, and is a list (i.e., a ManyToOne)
            if isinstance(getattr(copy, k, None), list):

                #
                # Delete each existing entity, because we're about to
                # override the value.
                #
                for i in getattr(copy, k):
                    i.delete()

            # Set the new (overridden) value
            setattr(copy, k, v)

        return copy

    def draft(self):
        """
        Used to create a new, unpublished draft of a recipe.
        """
        if self.current_draft:
            self.current_draft.delete()
            self.current_draft = None

        return self.duplicate({
            'published_version' : self
        })

    def publish(self):
        """
        Used to publish an orphan draft as a new recipe.
        """
        assert self.state == 'DRAFT', "Only drafts can be published."

        # If this recipe is a draft of another, merge the changes back in
        if self.published_version:
            return self.merge()

        # Otherwise, just set the state to PUBLISHED
        self.state = 'PUBLISHED'

    def merge(self):
        """
        Used to merge a drafted recipe's changes back into its source.
        """

        # Make sure this is a draft with a source recipe
        assert self.state == 'DRAFT', "Only drafts can be merged."
        source = self.published_version
        assert source is not None, "This recipe doesn't have a `published_version`."

        # Clone the draft onto the published version
        self.__copy_target__ = self.published_version
        deepcopy(self)

        # Delete the draft
        self.delete()

    @property
    def calculations(self):
        return Calculations(self)

    @property
    def efficiency(self):
        if self.author:
            return self.author.settings['brewhouse_efficiency']
        return .75

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
            self.slugs[-1].slug,
            '' if public else 'builder/'
        )

    @property
    def printable_type(self):
        return {
            'MASH'          : 'All Grain',
            'EXTRACT'       : 'Extract',
            'EXTRACTSTEEP'  : 'Extract with Steeped Grains',
            'MINIMASH'      : 'Extract with Mini-Mash'
        }[self.type]

    def touch(self):
        self.last_updated = datetime.utcnow()


class RecipeAddition(Entity, DeepCopyMixin):

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
                                'OUNCE',
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
    def pounds(self):
        if self.unit == 'POUND':
            return self.amount
        if self.unit == 'OUNCE':
            return self.amount / 16.0
        raise InvalidUnitException('Could not convert `%s` to pounds.' % self.unit)

    @property
    def minutes(self):
        if self.duration is None:
            return 0
        return self.duration.seconds / 60

    @property
    def sortable_minutes(self):
        if self.use == 'FIRST WORT':
            return maxint

        if self.use in ('POST BOIL', 'FLAME-OUT'):
            return -1

        return self.minutes

    @property
    def step(self):
        return ({
            'MASH'          : 'mash',
            'FIRST WORT'    : 'boil',
            'BOIL'          : 'boil',
            'POST-BOIL'     : 'boil',
            'FLAME OUT'     : 'boil',
            'PRIMARY'       : 'fermentation',
            'SECONDARY'     : 'fermentation',
            'TERTIARY'      : 'fermentation'
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

    @property
    def eta(self):
        """
        The number of minutes (after the boil starts) at which to add
        the hop addition.

        For a 15 minute addition in a 60 minute boil, the `eta` would be 45m
        """
        offset = self.recipe.boil_minutes - self.minutes
        return '%sm' % offset



class FermentationStep(Entity, DeepCopyMixin):

    STEPS = (
        'PRIMARY',
        'SECONDARY',
        'TERTIARY'
    )

    step            = Field(Enum(*STEPS))
    days            = Field(Integer)
    fahrenheit      = Field(Float)

    recipe          = ManyToOne('Recipe', inverse='fermentation_steps')


class RecipeView(Entity):

    datetime        = Field(DateTime, default=datetime.utcnow())

    recipe          = ManyToOne('Recipe', inverse='views')
