from pecan                                      import expose, request, abort
from pecan.rest                                 import RestController
from draughtcraft                               import model
from draughtcraft.lib.schemas.recipes.builder   import RecipeChange, RecipeAddition
from elixir                                     import entities
from datetime                                   import timedelta


class RecipeBuilderAsyncController(RestController):

    def __rendered__(self):
        return dict(
            recipe = request.context['recipe']
        )

    @expose('recipes/builder/async.html')
    def get_all(self):
        return self.__rendered__()

    @expose('recipes/builder/async.html')
    def delete(self, id):
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


class RecipeBuilderController(object):

    @expose('recipes/builder/index.html')
    def index(self):
        return dict()

    async = RecipeBuilderAsyncController()

