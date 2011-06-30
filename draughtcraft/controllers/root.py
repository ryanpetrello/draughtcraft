from pecan                              import expose, request
from draughtcraft.lib.schemas.login     import LoginSchema

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
        method          = 'POST',
        schema          = LoginSchema(),
        htmlfill        = dict(auto_insert_errors = True, prefix_error = True),
        error_handler   = lambda: request.path
    )
    def _post_login(self, username, password):

        print username
        print password
        
        return dict()

    error   = ErrorController()
    recipes = RecipesController()
    signup  = SignupController()
