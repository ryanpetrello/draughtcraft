from pecan                              import expose, request, redirect
from draughtcraft.lib.schemas.signup    import SignupSchema

class SignupController(object):

    @expose(
        generic     = True,
        template    = 'signup/index.html'
    )
    def index(self):
        return dict()

    @index.when(
        method          = 'POST',
        schema          = SignupSchema(),
        htmlfill        = dict(auto_insert_errors = True, prefix_error = True),
        error_handler   = lambda: request.path
    )
    def _post(self, username, password, password_confirm, email):
        redirect('/recipes/create')
