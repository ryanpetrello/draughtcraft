from pecan import expose

from error      import ErrorController
from recipes    import RecipesController

class RootController(object):

    @expose('index.html')
    def index(self):
        return dict()

    recipes = RecipesController()
    error   = ErrorController()
