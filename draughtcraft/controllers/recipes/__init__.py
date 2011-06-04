from pecan              import expose, redirect, request, abort
from pecan.decorators   import transactional
from draughtcraft       import model
from builder            import RecipeBuilderController


class SlugController(object):

    def __init__(self, slug):
        self.slug = slug

    builder = RecipeBuilderController()


class RecipeController(object):
    
    @expose()
    def _lookup(self, slug, *remainder):
        return SlugController(slug), remainder

    def __init__(self, recipeID):
        recipe = model.Recipe.get(int(recipeID))
        if recipe is None:
            abort(404)

        request.context['recipe'] = recipe
    

class RecipesController(object):

    @expose()
    def _lookup(self, recipeID, *remainder):
        return RecipeController(recipeID), remainder

    @expose()
    @transactional()
    def create(self):
        recipe = model.Recipe()
        recipe.flush()

        redirect('/recipes/%d/american-ale/builder' % recipe.id)
