from pecan import expose, request, response, redirect
from pecan.ext.wtforms import with_form
from draughtcraft.lib.notice import notify
from draughtcraft.lib.forms.settings.password import UserPasswordForm


class PasswordController(object):

    @expose(generic=True, template='settings/password.html')
    @with_form(UserPasswordForm)
    def index(self):
        return dict(
            user=request.context['user']
        )

    @index.when(method='POST')
    @with_form(UserPasswordForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def index_post(self, **kw):
        user = request.context['user']
        user.password = kw['password']

        notify('Your password has been changed.')
        redirect('/settings/password', headers=response.headers)
