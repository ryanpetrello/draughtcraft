from pecan                              import expose, request, redirect
from draughtcraft                       import model
from draughtcraft.lib.auth              import remove_trial_recipe
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

        user = model.User(
            username    = username,
            password    = password,
            email       = email
        )

        if request.context['trial_recipe']:
            request.context['trial_recipe'].author = user
            remove_trial_recipe()

        redirect('/recipes/create')
