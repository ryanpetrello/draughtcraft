from pecan import expose, request, response, redirect
from pecan.ext.wtforms import with_form
from draughtcraft.lib.units import to_us
from draughtcraft.lib.notice import notify
from draughtcraft.lib.forms.settings.recipe import UserRecipeForm


class RecipeController(object):

    @expose(generic=True, template='settings/recipe.html')
    @with_form(UserRecipeForm)
    def index(self):
        form = request.pecan['form']
        user = request.context['user']
        form.process(**{
            'unit_system': user.settings['unit_system'],
            'default_recipe_type': user.settings['default_recipe_type'],
            'default_ibu_formula': user.settings['default_ibu_formula']
        })

        return dict(
            form=form,
            user=user
        )

    @index.when(method='POST')
    @with_form(UserRecipeForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def index_post(self, **kw):
        user = request.context['user']

        for k, v in kw.items():
            user.settings[k] = v

        if request.context['metric'] == True:
            user.settings['default_recipe_volume'] = to_us(
                *(user.settings['default_recipe_volume'], 'LITER')
            )[0]

        user.settings['brewhouse_efficiency'] /= 100.00

        notify('Your settings have been saved.')
        redirect('/settings/recipe', headers=response.headers)
