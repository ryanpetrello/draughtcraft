from pecan                                          import expose, request, redirect
from pecan.rest                                     import RestController
from pecan.ext.wtforms                              import with_form
from draughtcraft                                   import model
from draughtcraft.lib.auth                          import save_trial_recipe
from draughtcraft.lib.units                         import to_us
from draughtcraft.lib.forms.recipes.create          import RecipeCreationForm

class RecipeCreationController(RestController):

    @expose('recipes/create.html')
    @with_form(RecipeCreationForm)
    def get_all(self):
        #
        # If you're not logged in, and you already have a trial recipe,
        # redirect to *that* recipe so you can't create another one.
        #
        recipe = request.context['trial_recipe'] 
        if request.context['user'] is None and recipe is not None:
            redirect(recipe.url(public=False)) 

        return dict()

    @expose('json')
    @with_form(RecipeCreationForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def post(self, **kw):
        recipe = model.Recipe(
            name        = kw.get('name'),
            type        = kw.get('type'),
            author      = request.context['user']
        )

        if recipe.metric:
            recipe.gallons = to_us(*(kw.get('volume'), 'LITER'))[0]
        else:
            recipe.gallons = kw.get('volume')

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
        if recipe.author and len(recipe.author.recipes) == 1:
            recipe.author.settings['default_recipe_type'] = recipe.type
            recipe.author.settings['default_recipe_volume'] = recipe.gallons

        redirect('/recipes/%x/%s/builder/' % (recipe.id, recipe.slugs[0].slug))
