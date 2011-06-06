from pecan          import expose, redirect
from pecan.rest     import RestController
from draughtcraft   import model

class RecipeCreationController(RestController):

    @expose('recipes/create.html')
    def index(self):
        return dict()

    @expose()
    def post(self):
        recipe = model.Recipe()
        recipe.flush()

        redirect('/recipes/%d/american-ale/builder' % recipe.id)
