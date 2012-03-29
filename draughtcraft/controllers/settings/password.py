from pecan                                      import (expose, request,
                                                        response, redirect)
from draughtcraft.lib.notice                    import notify
from draughtcraft.lib.schemas.settings.password import UserPasswordSchema


class PasswordController(object):

    @expose(
        generic     = True,
        template    = 'settings/password.html'
    )
    def index(self):
        return dict(
            user = request.context['user']
        )

    @index.when(
        method              = 'POST',
        #schema              = UserPasswordSchema(),
        #error_handler       = lambda: request.path,
        #htmlfill            = dict(auto_insert_errors = True, prefix_error = False)
    )
    def index_post(self, **kw):
        user = request.context['user']
        user.password = kw['password']

        notify('Your password has been changed.')
        redirect('/settings/password', headers=response.headers)
