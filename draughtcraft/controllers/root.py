from pecan                              import expose, request, redirect
from draughtcraft                       import model
from draughtcraft.lib.auth              import (save_user_session, 
                                                remove_user_session, 
                                                remove_trial_recipe)
from draughtcraft.lib.schemas.login     import LoginSchema

from error      import ErrorController
from profile    import ProfilesController
from recipes    import RecipesController
from settings   import SettingsController
from signup     import SignupController

class RootController(object):

    @expose('index.html')
    def index(self):
        if request.context['user']:
            redirect('/profile/%s' % request.context['user'].username)
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
        user = model.User.get_by(username=username)
        save_user_session(user)

        if request.context['trial_recipe']:
            request.context['trial_recipe'].author = user
            remove_trial_recipe()

        redirect('/')

    @expose()
    def logout(self):
        remove_user_session()
        redirect('/')

    error       = ErrorController()
    profile     = ProfilesController()
    recipes     = RecipesController()
    settings    = SettingsController()
    signup      = SignupController()
