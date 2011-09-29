from pecan                              import expose, request, redirect, abort
from draughtcraft                       import model
from draughtcraft.lib.auth              import (save_user_session, 
                                                remove_user_session, 
                                                remove_trial_recipe)
from draughtcraft.lib.schemas.login     import LoginSchema

from error          import ErrorController
from forgot         import ForgotPasswordController
from ingredients    import IngredientsController
from profile        import ProfilesController
from recipes        import RecipesController
from settings       import SettingsController
from signup         import SignupController

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
    def login(self, **kw):
        return dict(welcome = 'welcome' in kw)

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

    @expose('browser.html')
    def browser(self):
        return dict()

    """
    Anonymous shortcut for toggling US/Metric units (usable by visitors).
    """
    @expose(generic=True)
    def units(self):
        abort(405)

    @units.when(method="POST", template='json')
    def _toggle_units(self, **kw):
        if request.context['user'] is None:
            session = request.environ['beaker.session']
            session['metric'] = not session.get('metric', False)
            session.save()
        return dict()

    error       = ErrorController()
    forgot      = ForgotPasswordController()
    ingredients = IngredientsController()
    profile     = ProfilesController()
    recipes     = RecipesController()
    settings    = SettingsController()
    signup      = SignupController()
