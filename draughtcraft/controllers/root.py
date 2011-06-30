from pecan import expose

from error      import ErrorController
from recipes    import RecipesController
from signup     import SignupController

class RootController(object):

    @expose('index.html')
    def index(self):
        return dict()

    @expose(
        generic     = True,
        template    = 'login.html'
    )
    def login(self):
        return dict()

    @login.when(
        method      = 'POST'
    )
    def _post_login(self, username, password):
        return dict()

    error   = ErrorController()
    recipes = RecipesController()
    signup  = SignupController()
