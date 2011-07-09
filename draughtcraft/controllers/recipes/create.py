from pecan                                          import expose, request, redirect
from pecan.rest                                     import RestController
from draughtcraft                                   import model
from draughtcraft.lib.auth                          import save_trial_recipe
from draughtcraft.lib.schemas.recipes.create        import RecipeCreation

class RecipeCreationController(RestController):

    @expose('recipes/create.html')
    def get_all(self):
        #
        # If you're not logged in, and you already have a trial recipe,
        # redirect to *that* recipe so you can't create another one.
        #
        recipe = request.context['trial_recipe'] 
        if request.context['user'] is None and recipe is not None:
            redirect(recipe.url(public=False)) 

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

        #
        # If the recipe is created by a guest instead of an authenticated
        # user, store the trial recipe in a cookie.
        #
        if recipe.author is None:
            save_trial_recipe(recipe)

        #
        # If we have an authenticated user, and this is their first recipe,
        # save their choices as defaults so they'll be used again on their
        # next recipe.
        #
        if recipe.author:
            recipe.author.settings['default_recipe_type'] = recipe.type
            recipe.author.settings['default_recipe_volume'] = recipe.gallons

        redirect('/recipes/%d/%s/builder/' % (recipe.id, recipe.slugs[0].slug))
