from pecan                                  import expose, request, redirect, abort
from pecan.rest                             import RestController
from elixir                                 import entities
from beerparts.lib.schemas.recipes.builder  import RecipeAdditionSchema


class RecipeBuilderAsyncController(RestController):

    def __rendered__(self):
        return dict(
            recipe = request.context['recipe']
        )

    @expose('recipes/builder/async.html')
    def get_all(self):
        return self.__rendered__()

    @expose('recipes/builder/async.html')
    def put(self, **kw):
        from pprint import pprint
        pprint(kw)
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

