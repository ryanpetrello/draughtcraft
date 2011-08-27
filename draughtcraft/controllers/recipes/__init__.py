from pecan              import expose, request, abort, redirect
from draughtcraft       import model
from create             import RecipeCreationController
from builder            import RecipeBuilderController


class SlugController(object):

    def __init__(self, slug):
        self.slug = slug

        # Make sure the provided slug is valid
        if slug not in [slug.slug for slug in request.context['recipe'].slugs]:
            abort(404)

    @expose('recipes/builder/index.html')
    def index(self):
        recipe = request.context['recipe']
        if recipe.state != "PUBLISHED":
            abort(404)
        return dict(
            recipe      = recipe,
            editable    = False
        )

    @expose(generic=True)
    def async(self): pass

    @async.when(
        method      = 'POST',
        template    = 'recipes/builder/async.html'
    )
    def do_async(self):
        recipe = request.context['recipe']
        if recipe.state != "PUBLISHED":
            abort(404)

        # Log a view for the recipe
        model.RecipeView(recipe = recipe)

        return dict(recipe = recipe)

    @expose(generic=True)
    def draft(self): pass

    @draft.when(method="POST")
    def do_draft(self):
        source = request.context['recipe']
        if source.author is None or source.author != request.context['user']:
            abort(401)
        if source.state != "PUBLISHED":
            abort(401)

        draft = source.draft()
        draft.flush()
        redirect("%sbuilder" % draft.url())

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

    create = RecipeCreationController()
