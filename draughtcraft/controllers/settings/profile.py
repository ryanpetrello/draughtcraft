from pecan import expose, request, response, redirect
from pecan.ext.wtforms import with_form
from draughtcraft.lib.notice import notify
from draughtcraft.lib.forms.settings.profile import UserProfileForm


class ProfileController(object):

    @expose(generic=True, template='settings/profile.html')
    @with_form(UserProfileForm)
    def index(self):
        return dict(
            user=request.context['user']
        )

    @index.when(method='POST')
    @with_form(UserProfileForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def index_post(self, **kw):
        user = request.context['user']

        for k, v in kw.items():
            setattr(user, k, v)

        notify('Your settings have been saved.')
        redirect('/settings/profile', headers=response.headers)
