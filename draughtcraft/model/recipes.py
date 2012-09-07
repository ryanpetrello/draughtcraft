from pecan import request
from elixir import (
    Entity, Field, Unicode, UnicodeText, Integer, Interval, Float, Enum,
    DateTime, using_options, OneToMany, ManyToOne, OneToOne, entities
)
from draughtcraft.lib.calculations import Calculations
from draughtcraft.lib.units import (UnitConvert, InvalidUnitException,
                                    to_us, to_metric, to_kg, to_l)
from draughtcraft.model.deepcopy import DeepCopyMixin, ShallowCopyMixin
from datetime import datetime
from copy import deepcopy
from sys import maxint

import string


class Recipe(Entity, DeepCopyMixin, ShallowCopyMixin):

    TYPES = (
        'MASH',
        'EXTRACT',
        'EXTRACTSTEEP',
        'MINIMASH'
    )

    MASH_METHODS = (
        'SINGLESTEP',
        'TEMPERATURE',
        'DECOCTION',
        'MULTISTEP'
    )

    STATES = (
        'DRAFT',
        'PUBLISHED'
    )

    type = Field(
        Enum(*TYPES, native_enum=False), default='MASH', index=True)
    name = Field(Unicode(256), index=True)
    gallons = Field(Float, default=5)
    boil_minutes = Field(Integer, default=60)
    notes = Field(UnicodeText)
    creation_date = Field(DateTime, default=datetime.utcnow)
    last_updated = Field(DateTime, default=datetime.utcnow, index=True)

    # Cached statistics
    _og = Field(Float, colname='og')
    _fg = Field(Float, colname='fg')
    _abv = Field(Float, colname='abv')
    _srm = Field(Integer, colname='srm')
    _ibu = Field(Integer, colname='ibu')

    mash_method = Field(
        Enum(*MASH_METHODS, native_enum=False), default='SINGLESTEP')
    mash_instructions = Field(UnicodeText)

    state = Field(
        Enum(*STATES, native_enum=False), default='DRAFT')
    current_draft = ManyToOne('Recipe', inverse='published_version')
    published_version = OneToOne(
        'Recipe', inverse='current_draft', order_by='creation_date')

    copied_from = ManyToOne('Recipe', inverse='copies')
    copies = OneToMany(
        'Recipe', inverse='copied_from', order_by='creation_date')

    views = OneToMany(
        'RecipeView', inverse='recipe', cascade='all, delete-orphan')
    additions = OneToMany(
        'RecipeAddition', inverse='recipe', cascade='all, delete-orphan')
    fermentation_steps = OneToMany(
        'FermentationStep',
        inverse='recipe',
        order_by='step',
        cascade='all, delete-orphan'
    )
    slugs = OneToMany('RecipeSlug', inverse='recipe', order_by='id',
                      cascade='all, delete-orphan')
    style = ManyToOne('Style', inverse='recipes')
    author = ManyToOne('User', inverse='recipes')

    __ignored_properties__ = (
        'current_draft',
        'published_version',
        'copies',
        'views',
        'creation_date',
        'state',
        '_og',
        '_fg',
        '_abv',
        '_srm',
        '_ibu'
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
        for k, v in overrides.items():

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
            'published_version': self
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

        # Store cached values
        self._og = self.calculations.og
        self._fg = self.calculations.fg
        self._abv = self.calculations.abv
        self._srm = self.calculations.srm
        self._ibu = self.calculations.ibu

        # Generate a new slug if the existing one hasn't changed.
        existing = [slug.slug for slug in self.slugs]
        if entities.RecipeSlug.to_slug(self.name) not in existing:
            self.slugs.append(entities.RecipeSlug(name=self.name))

    def merge(self):
        """
        Used to merge a drafted recipe's changes back into its source.
        """

        # Make sure this is a draft with a source recipe
        assert self.state == 'DRAFT', "Only drafts can be merged."
        source = self.published_version
        assert source is not None, \
            "This recipe doesn't have a `published_version`."

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

    @property
    def unit_system(self):
        if request.context['metric'] is True:
            return 'METRIC'
        return 'US'

    @property
    def metric(self):
        return self.unit_system == 'METRIC'

    @property
    def liters(self):
        liters = to_metric(*(self.gallons, "GALLON"))[0]
        return round(liters, 3)

    @liters.setter  # noqa
    def liters(self, v):
        gallons = to_us(*(v, "LITER"))[0]
        self.gallons = gallons

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
                    percentages[addition] = float(
                        addition.amount) / float(total)
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
        return self._partition([
            a for a in self.additions if a.step == 'fermentation'
        ])

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
            1: 'SECONDARY',
            2: 'TERTIARY'
        }.get(total, None)

    def url(self, public=True):
        """
        The URL for a recipe.
        """
        return '/recipes/%s/%s/%s' % (
            ('%x' % self.id).lower(),
            self.slugs[-1].slug,
            '' if public else 'builder'
        )

    @property
    def printable_type(self):
        return {
            'MASH': 'All Grain',
            'EXTRACT': 'Extract',
            'EXTRACTSTEEP': 'Extract w/ Steeped Grains',
            'MINIMASH': 'Mini-Mash'
        }[self.type]

    def touch(self):
        self.last_updated = datetime.utcnow()

    @property
    def og(self):
        return self._og

    @property
    def fg(self):
        return self._fg

    @property
    def abv(self):
        return self._abv

    @property
    def srm(self):
        return self._srm

    @property
    def ibu(self):
        return self._ibu

    def to_xml(self):
        from draughtcraft.lib.beerxml import export
        kw = {
            'name': self.name,
            'type': {
                'MASH': 'All Grain',
                'MINIMASH': 'Partial Mash'
            }.get(self.type, 'Extract'),
            'brewer': self.author.printed_name,
            'batch_size': self.liters,
            'boil_size': self.liters * 1.25,
            'boil_time': self.boil_minutes,
            'notes': self.notes,
            'fermentation_stages': len(self.fermentation_steps),
        }

        hops = [a.to_xml() for a in self.additions if a.hop]
        fermentables = [a.to_xml() for a in self.additions if a.fermentable]
        yeast = [a.to_xml() for a in self.additions if a.yeast]
        extras = [a.to_xml() for a in self.additions if a.extra]

        kw['hops'] = hops
        kw['fermentables'] = fermentables
        kw['yeasts'] = yeast
        kw['miscs'] = extras

        kw['mash'] = []
        kw['waters'] = []

        if self.style is None:
            kw['style'] = export.Style(
                name='',
                category='No Style Chosen',
                type='None',
                category_number=0,
                style_letter='',
                og_min=0,
                og_max=0,
                ibu_min=0,
                ibu_max=0,
                color_min=0,
                color_max=0,
                fg_min=0,
                fg_max=0
            )
        else:
            kw['style'] = self.style.to_xml()

        if self.type != 'EXTRACT':
            kw['efficiency'] = self.efficiency * 100.00

        for stage in self.fermentation_steps:
            if stage.step == 'PRIMARY':
                kw['primary_age'] = stage.days
                kw['primary_temp'] = stage.celsius
            if stage.step == 'SECONDARY':
                kw['secondary_age'] = stage.days
                kw['secondary_temp'] = stage.celsius
            if stage.step == 'TERTIARY':
                kw['tertiary_age'] = stage.days
                kw['tertiary_temp'] = stage.celsius

        return export.Recipe(**kw).render()

    def __json__(self):
        from draughtcraft.templates.helpers import alphanum_key

        def inventory(cls, types=[]):
            return sorted([
                f.__json__() for f in cls.query.all()
                if not types or (types and f.type in types)
            ], key=lambda f: alphanum_key(f['name']))

        #
        # Attempt to look up the preferred calculation method for the
        # recipe's author.
        #
        ibu_method = 'tinseth'
        user = self.author
        if user:
            ibu_method = user.settings.get('default_ibu_formula', 'tinseth')

        return {
            # Basic attributes
            'name': self.name,
            'style': self.style.id if self.style else None,
            'gallons': self.gallons,

            # Ingredients
            'mash': filter(
                lambda a: a.step == 'mash',
                self.additions
            ),
            'boil': filter(
                lambda a: a.step == 'boil',
                self.additions
            ),
            'fermentation': filter(
                lambda a: a.step == 'fermentation',
                self.additions
            ),

            'ibu_method': ibu_method,
            'efficiency': self.efficiency,

            # Inventory
            'inventory': {
                'malts': inventory(
                    entities.Fermentable,
                    ('MALT', 'GRAIN', 'ADJUNCT', 'SUGAR')
                ),
                'extracts': inventory(
                    entities.Fermentable,
                    ('EXTRACT',)
                ),
                'hops': inventory(entities.Hop),
                'yeast': inventory(entities.Yeast),
                'extras': inventory(entities.Extra)
            },

            # Extras
            'mash_method': self.mash_method,
            'mash_instructions': self.mash_instructions,
            'boil_minutes': self.boil_minutes,
            'fermentation_steps': self.fermentation_steps,
            'notes': self.notes,

            'metric': self.metric
        }


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

    amount = Field(Float)

    #
    # At the database level, only certain units are actually stored.
    # We do this for the sake of uniformity (to make calculations easier).
    #
    unit = Field(Enum(*[
                      'POUND',
                      'OUNCE',
                      'TEASPOON',
                      'TABLESPOON',
                      'GALLON',
                      'LITER'
                      ], native_enum=False), nullable=True)

    use = Field(Enum(*USES, native_enum=False))
    duration = Field(Interval)

    recipe = ManyToOne('Recipe', inverse='additions')
    fermentable = ManyToOne('Fermentable', inverse='additions')
    hop = ManyToOne('Hop', inverse='additions')
    yeast = ManyToOne('Yeast', inverse='additions')
    extra = ManyToOne('Extra', inverse='extra')

    @property
    def printable_amount(self):
        if getattr(self.recipe, 'unit_system', None) == 'METRIC':
            return UnitConvert.to_str(*to_metric(self.amount, self.unit))

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
        raise InvalidUnitException(
            'Could not convert `%s` to pounds.' % self.unit)

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
            'MASH': 'mash',
            'FIRST WORT': 'boil',
            'BOIL': 'boil',
            'POST-BOIL': 'boil',
            'FLAME OUT': 'boil',
            'PRIMARY': 'fermentation',
            'SECONDARY': 'fermentation',
            'TERTIARY': 'fermentation'
        })[self.use]

    @property
    def percentage(self):
        additions = getattr(self.recipe, self.step)
        return self.recipe._percent(additions).get(self, 0)

    def to_xml(self):
        from draughtcraft.lib.beerxml import export

        if self.hop:

            kw = {
                'name': self.hop.name,
                'alpha': self.hop.alpha_acid,
                'amount': to_kg(self.amount, self.unit),
                'time': self.minutes,
                'notes': self.hop.description,
                'form': self.form.capitalize(),
                'origin': self.hop.printed_origin
            }

            kw['use'] = {
                'MASH': 'Mash',
                'FIRST WORT': 'First Wort',
                'BOIL': 'Boil',
                'POST-BOIL': 'Aroma',
                'FLAME OUT': 'Aroma',
                'PRIMARY': 'Dry Hop',
                'SECONDARY': 'Dry Hop',
                'TERTIARY': 'Dry Hop'
            }.get(self.use)

            return export.Hop(**kw)

        if self.fermentable:
            kw = {
                'name': self.fermentable.name,
                'amount': to_kg(self.amount, self.unit),
                'yield': self.fermentable.percent_yield,
                'color': self.fermentable.lovibond,
                'add_after_boil': self.step == 'fermentation',
                'origin': self.fermentable.printed_origin,
                'notes': self.fermentable.description
            }

            kw['type'] = {
                'MALT': 'Grain',
                'GRAIN': 'Grain',
                'ADJUNCT': 'Adjunct',
                'EXTRACT': 'Extract',
                'SUGAR': 'Sugar'
            }.get(self.fermentable.type)

            if self.fermentable.type == 'EXTRACT' and \
                    'DME' in self.fermentable.name:
                kw['type'] = 'Dry Extract'

            return export.Fermentable(**kw)

        if self.yeast:
            kw = {
                'name': self.yeast.name,
                'form': self.yeast.form.capitalize(),
                'attenuation': self.yeast.attenuation * 100.00,
                'notes': self.yeast.description
            }

            # Map types as appropriately as possible to BeerXML <TYPE>'s.
            kw['type'] = {
                'ALE': 'Ale',
                'LAGER': 'Lager',
                'WILD': 'Ale',
                'MEAD': 'Wine',
                'CIDER': 'Wine',
                'WINE': 'Wine'
            }.get(self.yeast.type)

            if self.yeast.form == 'LIQUID':
                #
                # If the yeast is liquid, it's probably a activator/vial.  For
                # simplicity, we'll assume Wyeast's volume, 125ml.
                #
                kw['amount'] = 0.125
            else:
                #
                # If the yeast is dry, it's probably a small packet.  For
                # simplicity, we'll assume a standard weight of 11.5g.
                #
                kw['amount'] = 0.0115
                kw['amount_is_weight'] = True

            if self.use in ('SECONDARY', 'TERTIARY'):
                kw['add_to_secondary'] = True

            return export.Yeast(**kw)

        if self.extra:
            kw = {
                'name': self.extra.name,
                'type': string.capwords(self.extra.type),
                'time': self.minutes,
                'notes': self.extra.description
            }

            kw['use'] = {
                'MASH': 'Mash',
                'FIRST WORT': 'Boil',
                'BOIL': 'Boil',
                'POST-BOIL': 'Boil',
                'FLAME OUT': 'Boil',
                'PRIMARY': 'Primary',
                'SECONDARY': 'Secondary',
                'TERTIARY': 'Secondary'
            }.get(self.use)

            if self.unit is None:
                #
                # If there's no unit (meaning it's just one "unit"), assume
                # a weight of 15 grams.
                #
                kw['amount'] = 0.015
                kw['amount_is_weight'] = True
            elif self.extra.liquid:
                kw['amount'] = to_l(self.amount, self.unit)
            else:
                kw['amount'] = to_kg(self.amount, self.unit)
                kw['amount_is_weight'] = True

            return export.Misc(**kw)

    def __json__(self):
        return {
            'amount': self.amount,
            'unit': self.unit,
            'use': self.use,
            'minutes': self.minutes,
            'ingredient': self.ingredient
        }


class HopAddition(RecipeAddition):

    FORMS = (
        'LEAF',
        'PELLET',
        'PLUG'
    )

    form = Field(
        Enum(*FORMS, native_enum=False), default='LEAF')
    alpha_acid = Field(Float())

    using_options(inheritance='multi', polymorphic=True)

    @property
    def printable_amount(self):
        unit = self.unit
        if self.amount == 0:
            unit = 'OUNCE'
        if getattr(self.recipe, 'unit_system', None) == 'METRIC':
            return UnitConvert.to_str(*to_metric(self.amount, unit))
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

    def __json__(self):
        json = super(HopAddition, self).__json__()
        json.update({
            'form': self.form,
            'alpha_acid': self.alpha_acid
        })
        return json


class FermentationStep(Entity, DeepCopyMixin):

    STEPS = (
        'PRIMARY',
        'SECONDARY',
        'TERTIARY'
    )

    step = Field(Enum(*STEPS, native_enum=False))
    days = Field(Integer)
    fahrenheit = Field(Float)

    recipe = ManyToOne('Recipe', inverse='fermentation_steps')

    @property
    def celsius(self):
        return round((5 / 9.0) * (self.fahrenheit - 32))

    @celsius.setter  # noqa
    def celsius(self, v):
        self.fahrenheit = ((9 / 5.0) * v) + 32

    def __json__(self):
        json = {
            'step': self.step,
            'days': self.days,
            'fahrenheit': self.fahrenheit
        }
        return json


class RecipeView(Entity):

    datetime = Field(DateTime, default=datetime.utcnow())

    recipe = ManyToOne('Recipe', inverse='views')
