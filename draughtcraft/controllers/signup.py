from pecan                              import expose, request, conf
from pecan.decorators                   import after_commit
from draughtcraft                       import model
from draughtcraft.lib.auth              import remove_trial_recipe
from draughtcraft.lib                   import email as emaillib
from draughtcraft.lib.schemas.signup    import SignupSchema

import pecan

def send_signup_email():
    if not request.pecan['validation_errors']:
        emaillib.send(
            request.context['__signup_email__'],
            'signup',
            'Welcome to DraughtCraft',
            {'username': request.context['__signup_username__']},
            bcc = [conf.signups.bcc]
        )


class SignupController(object):

    @expose(
        generic     = True,
        template    = 'signup/index.html'
    )
    def index(self):
        return dict()

    @index.when(
        method          = 'POST',
        #schema          = SignupSchema(),
        #htmlfill        = dict(auto_insert_errors = True, prefix_error = True),
        #error_handler   = lambda: request.path
    )
    @after_commit(send_signup_email)
    def _post(self, username, password, password_confirm, email):

        user = model.User(
            username    = username,
            password    = password,
            email       = email
        )

        if request.context['trial_recipe']:
            request.context['trial_recipe'].author = user
            remove_trial_recipe()

        request.context['__signup_email__'] = email
        request.context['__signup_username__'] = username

        pecan.redirect('/login?welcome')
