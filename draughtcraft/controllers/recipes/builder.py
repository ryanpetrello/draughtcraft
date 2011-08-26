from pecan                                      import (expose, request, abort,
                                                        redirect)
from pecan.secure                               import SecureController
from pecan.rest                                 import RestController
from draughtcraft                               import model
from draughtcraft.lib.schemas.recipes.builder   import (
                                                        RecipeChange, 
                                                        RecipeAddition,
                                                        RecipeStyle,
                                                        RecipeBoilMinutes,
                                                        RecipeVolume,
                                                        RecipeNotes,
                                                        FermentationStepUpdate
                                                        )
from elixir                                     import entities
from datetime                                   import timedelta


class FermentationStepsController(RestController):
    """
    Used to modify, add, and remove the recipe's fermentation schedule
    (e.g., Primary, Secondary, length and temperatures...)
    """

    @property
    def recipe(self):
        return request.context['recipe']

    @expose('recipes/builder/async.html')
    def post(self):
        """
        Used to add the next applicable fermentation step to the recipe.
        """
        last_step = self.recipe.fermentation_steps[-1]
        self.recipe.fermentation_steps.append(
            model.FermentationStep(
                step        = self.recipe.next_fermentation_step,
                days        = last_step.days,
                fahrenheit  = last_step.fahrenheit
            )
        )
        self.recipe.touch()
        return dict(recipe = self.recipe)

    @expose(
        'recipes/builder/async.html',
        schema = FermentationStepUpdate()
    )
    def put(self, step, **kw):
        """
        Used to update an existing fermentation step's parameters (e.g.,
        duration, temperature).
        """
        step.days = kw['days']
        step.fahrenheit = kw['temperature']
        self.recipe.touch()
        return dict(recipe = self.recipe)

    @expose('recipes/builder/async.html')
    def delete(self):
        if len(self.recipe.fermentation_steps) > 1:
            step = self.recipe.fermentation_steps[-1]
            self.recipe.fermentation_steps.remove(step)
            step.delete()
        return dict(recipe = self.recipe)


class RecipeSettingsController(object):
    """
    Used to change various settings for a recipe, such as batch size,
    target BJCP style, etc...
    """

    @property
    def recipe(self):
        return request.context['recipe']

    #
    # BJCP Recipe Style
    #
    @expose(generic=True)
    def style(self): pass

    @style.when(
        method      = 'POST',
        template    = 'recipes/builder/async.html',
        schema      = RecipeStyle()
    )
    def _style(self, target):
        self.recipe.style = target
        self.recipe.touch()
        return dict(recipe = self.recipe)

    #
    # Recipe Batch/Volume
    #
    @expose(generic=True)
    def volume(self): pass

    @volume.when(
        method      = 'POST',
        template    = 'recipes/builder/async.html',
        schema      = RecipeVolume()
    )
    def _volume(self, volume, unit):
        self.recipe.gallons = volume
        self.recipe.touch()
        return dict(recipe = self.recipe)

    #
    # Recipe Batch/Volume
    #
    @expose(generic=True)
    def boil_minutes(self): pass

    @boil_minutes.when(
        method          = 'POST',
        template        = 'recipes/builder/async.html',
        schema          = RecipeBoilMinutes(),
        error_handler   = lambda: '%sasync/ingredients' % request.context['recipe'].url(public=False),
        htmlfill        = dict(
            auto_insert_errors  = True, 
            prefix_error        = False,
            encoding            = u'utf-8',
            force_defaults      = False
        )
    )
    def _boil_minutes(self, minutes):
        self.recipe.boil_minutes = minutes
        self.recipe.touch()
        return dict(recipe = self.recipe)

    #
    # Recipe Notes and Remarks
    #
    @expose(generic=True)
    def notes(self): return

    @notes.when(
        method      = 'POST',
        template    = 'recipes/builder/async.html',
        schema      = RecipeNotes()
    )
    def _notes(self, notes):
        self.recipe.notes = notes
        self.recipe.touch()
        return dict(recipe = self.recipe)


class IngredientsController(RestController):

    def __rendered__(self):
        return dict(
            recipe = request.context['recipe']
        )

    @expose('recipes/builder/async.html')
    def get_all(self):
        return self.__rendered__()

    @expose('recipes/builder/async.html')
    def delete(self, id):
        """
        Used to remove an ingredient from the recipe.
        """
        addition = model.RecipeAddition.get(int(id))
        if addition:
            addition.delete()
            addition.recipe.touch()
        return self.__rendered__()

    @expose(
        'recipes/builder/async.html',
        schema              = RecipeChange(),
        error_handler       = lambda: request.path,
        htmlfill            = dict(
            auto_insert_errors  = True, 
            prefix_error        = False,
            encoding            = u'utf-8',
            force_defaults      = False
        ),
        variable_decode     = True
    )
    def put(self, **kw):
        """
        Used to update the ingredients in the recipe.
        Contains a list of `additions` for which updated information is
        available.
        """
        
        keys = ('mash_additions', 'boil_additions', 'fermentation_additions')
        for addition_class in keys:
            additions = kw.get(addition_class)
            for row in additions:
                # Clean up the hash a bit
                row.pop('type')

                # Grab the addition record
                addition = row.pop('addition')

                #
                # Apply the amount and unit
                # (if a valid amount/unit combination
                # can be parsed from the user's entry)
                #
                if 'amount' in row:
                    pair = row.pop('amount')
                    if pair:
                        amount, unit = pair
                        addition.amount = amount
                        addition.unit = unit or addition.ingredient.default_unit
                
                #
                # For "First Wort" additions,
                # change the duration to the full length of the boil
                #
                # For "Flame Out" additions,
                # change the duration to 0 minutes.
                #
                if 'use' in row:
                    if row['use'] == 'FIRST WORT':
                        row['duration'] = timedelta(minutes=addition.recipe.boil_minutes)
                    elif row['use'] == 'FLAME OUT':
                        row['duration'] = timedelta(minutes=0)
                    elif not row['duration']:
                        row['duration'] = timedelta(minutes=addition.recipe.boil_minutes)

                for k,v in row.items():
                    if v is not None:
                        setattr(addition, k, v)

        request.context['recipe'].touch()
        return self.__rendered__()

    @expose(
        'recipes/builder/async.html',
        schema = RecipeAddition()
    )
    def post(self, **kw):
        """
        Used to add a new ingredient into the recipe.
        """
        if request.pecan.get('validation_errors'):
            abort(400)

        # Look up the addition entity by name
        cls = getattr(entities, kw.get('type'), None)

        # Clean up the namespace a bit
        kw.pop('type')
        ingredient = kw.pop('ingredient')

        unit = ingredient.default_unit
        kw['amount'] = 0
        kw['unit'] = unit

        #
        # If it's a hop addition, copy defaults for AA
        #
        if getattr(ingredient, 'alpha_acid', None):
            kw['alpha_acid'] = ingredient.alpha_acid

        #
        # Create the entity and assign the ingredient
        # to the correct attribute (e.g., `fermentable`,
        # `hop`, `yeast`)
        #
        entity = cls(**kw)
        setattr(entity, ingredient.row_type, ingredient)
        entity.recipe = request.context['recipe']

        request.context['recipe'].touch()
        return self.__rendered__()


class RecipeBuilderAsyncController(object):

    ingredients         = IngredientsController()
    fermentation_steps  = FermentationStepsController()
    settings            = RecipeSettingsController()

    @expose(generic=True)
    def name(self): pass

    @name.when(
        method      = 'POST',
        template    = 'json'
    )
    def do_name(self, name):
        # If the name has changed, generate a new slug
        recipe = request.context['recipe']
        if recipe.name != name:
            recipe.slugs.append(
                entities.RecipeSlug(name=name)
            )

        recipe.name = name
        return dict()

class RecipeBuilderController(SecureController):

    @classmethod
    def check_permissions(cls):
        recipe = request.context['recipe']
        if recipe.state != 'DRAFT':
            return False
        if recipe.author:
            return recipe.author == request.context['user']
        if recipe == request.context['trial_recipe']:
            return True
        return False

    @expose('recipes/builder/index.html')
    def index(self):
        return dict(recipe = request.context['recipe'])

    @expose(generic=True)
    def publish(self):
        pass

    @publish.when(method='POST')
    def do_publish(self):
        recipe = request.context['recipe']
        recipe.publish()
        redirect('/profile/%s' % recipe.author.username)

    async = RecipeBuilderAsyncController()

