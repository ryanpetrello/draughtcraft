from pecan              import expose, redirect, request, abort
from pecan.decorators   import transactional
from draughtcraft       import model
from builder            import RecipeBuilderController


class RecipeController(object):
    
    def __init__(self, recipeID):
        recipe = model.Recipe.get(int(recipeID))
        if recipe is None:
            abort(404)

        request.context['recipe'] = recipe

    builder = RecipeBuilderController()
    

class RecipesController(object):

    @expose()
    def _lookup(self, recipeID, *remainder):
        return RecipeController(recipeID), remainder

    @expose()
    @transactional()
    def create(self):
        recipe = model.Recipe()
        recipe.flush()

        redirect('/recipes/%d/builder' % recipe.id)
