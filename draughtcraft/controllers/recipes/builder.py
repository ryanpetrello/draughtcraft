from pecan                                      import expose, request, abort
from pecan.rest                                 import RestController
from draughtcraft                               import model
from draughtcraft.lib.schemas.recipes.builder   import (
                                                        RecipeChange, 
                                                        RecipeAddition,
                                                        RecipeStyle,
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
        return self.__rendered__()

    @expose(
        'recipes/builder/async.html',
        schema              = RecipeChange(),
        error_handler       = lambda: request.path,
        htmlfill            = dict(auto_insert_errors = True, prefix_error = False),
        variable_decode     = True
    )
    def put(self, **kw):
        """
        Used to update the ingredients in the recipe.
        Contains a list of `additions` for which updated information is
        available.
        """

        for row in kw.get('additions'):
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

        return self.__rendered__()


class RecipeBuilderAsyncController(object):

    ingredients         = IngredientsController()
    fermentation_steps  = FermentationStepsController()
    settings            = RecipeSettingsController()


class RecipeBuilderController(object):

    @expose('recipes/builder/index.html')
    def index(self):
        return dict(recipe = request.context['recipe'])

    async = RecipeBuilderAsyncController()

