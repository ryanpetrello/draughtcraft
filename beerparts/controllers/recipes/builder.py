from pecan                                      import expose, request, redirect, abort
from pecan.rest                                 import RestController
from draughtcraft.lib.schemas.recipes.builder   import RecipeChange
from elixir                                     import entities


class RecipeBuilderAsyncController(RestController):

    def __rendered__(self):
        return dict(
            recipe = request.context['recipe']
        )

    @expose('recipes/builder/async.html')
    def get_all(self):
        return self.__rendered__()

    @expose(
        'recipes/builder/async.html',
        schema              = RecipeChange(),
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
                    addition.unit = unit

            for k,v in row.items():
                setattr(addition, k, v)

        return self.__rendered__()

    @expose('recipes/builder/async.html')
        #schema = RecipeAdditionSchema()
    def post(self, **kw):
        from pprint import pprint
        pprint(kw)
        return self.__rendered__()

        if request.pecan.get('validation_errors'):
            abort(400)

        # Look up the addition entity by name
        cls = getattr(entities, kw.get('type'), None)

        # Clean up the namespace a bit
        kw.pop('type')
        ingredient = kw.pop('ingredient')

        #
        # Create the entity and assign the ingredient
        # to the correct attribute (e.g., `fermentable`,
        # `hop`, `yeast`)
        #
        entity = cls(**kw)
        setattr(entity, ingredient.row_type, ingredient)
        entity.recipe = request.context['recipe']

        redirect('/recipes/%d/builder' % request.context['recipe'].id)


class RecipeBuilderController(object):

    @expose('recipes/builder/index.html')
    def index(self):
        return dict()

    async = RecipeBuilderAsyncController()

