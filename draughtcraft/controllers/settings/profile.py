from pecan                                      import (expose, request,
                                                        response, redirect)
from draughtcraft.lib.notice                    import notify
from draughtcraft.lib.schemas.settings.profile  import UserProfileSchema


class ProfileController(object):

    @expose(
        generic     = True,
        template    = 'settings/profile.html'
    )
    def index(self):
        return dict(
            user = request.context['user']
        )

    @index.when(
        method              = 'POST',
        schema              = UserProfileSchema(),
        error_handler       = lambda: request.path,
        htmlfill            = dict(auto_insert_errors = True, prefix_error = False),
        variable_decode     = True
    )
    def index_post(self, **kw):
        user = request.context['user']

        for k,v in kw.items():
            setattr(user, k, v)

        notify('Your settings have been saved.')
        redirect('/settings/profile', headers=response.headers)
