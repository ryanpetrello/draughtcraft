from pecan                                          import expose, request, redirect
from pecan.rest                                     import RestController
from draughtcraft                                   import model
from draughtcraft.lib.schemas.recipes.create        import RecipeCreation

class RecipeCreationController(RestController):

    @expose('recipes/create.html')
    def get_all(self):
        return dict()

    @expose(
        'json',
        schema              = RecipeCreation(),
        error_handler       = lambda: request.path,
        htmlfill            = dict(auto_insert_errors = True, prefix_error = False)
    )
    def post(self, **kw):
        recipe = model.Recipe()
        recipe.name = kw.get('name')
        recipe.flush()

        redirect('/recipes/%d/american-ale/builder' % recipe.id)
