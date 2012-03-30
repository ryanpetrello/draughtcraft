from pecan                              import expose, request, conf
from pecan.decorators                   import after_commit
from pecan.ext.wtforms                  import with_form
from draughtcraft                       import model
from draughtcraft.lib.auth              import remove_trial_recipe
from draughtcraft.lib                   import email as emaillib
from draughtcraft.lib.forms.signup      import SignupForm

import pecan


def send_signup_email():

    if not len(request.pecan['form'].errors):
        emaillib.send(
            request.context['__signup_email__'],
            'signup',
            'Welcome to DraughtCraft',
            {'username': request.context['__signup_username__']},
            bcc=[conf.signups.bcc]
        )


class SignupController(object):

    @expose(generic=True, template='signup/index.html')
    @with_form(SignupForm)
    def index(self):
        return dict()

    @index.when(method='POST')
    @after_commit(send_signup_email)
    @with_form(SignupForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def _post(self, username, password, password_confirm, email):

        user = model.User(
            username=username,
            password=password,
            email=email
        )

        if request.context['trial_recipe']:
            request.context['trial_recipe'].author = user
            remove_trial_recipe()

        request.context['__signup_email__'] = email
        request.context['__signup_username__'] = username

        pecan.redirect('/login?welcome')
