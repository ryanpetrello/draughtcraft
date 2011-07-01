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
        recipe = model.Recipe(
            name        = kw.get('name'),
            gallons     = kw.get('volume'),
            type        = kw.get('type'),
            author      = request.context['user']
        )
        recipe.fermentation_steps.append(
            model.FermentationStep(
                step = 'PRIMARY',
                days = 7,
                fahrenheit = 65
            )
        )
        recipe.flush()

        redirect('/recipes/%d/%s/builder' % (recipe.id, recipe.slugs[0].slug))
