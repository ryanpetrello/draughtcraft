from pecan import expose

from error      import ErrorController
from recipes    import RecipesController
from signup     import SignupController

class RootController(object):

    @expose('index.html')
    def index(self):
        return dict()

    error   = ErrorController()
    recipes = RecipesController()
    signup  = SignupController()
