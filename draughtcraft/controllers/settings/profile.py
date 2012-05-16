from pecan import expose, request, response, redirect
from pecan.ext.wtforms import with_form
from draughtcraft.lib.notice import notify
from draughtcraft.lib.forms.settings.profile import UserProfileForm


class ProfileController(object):

    @expose(generic=True, template='settings/profile.html')
    @with_form(UserProfileForm)
    def index(self):
        user = request.context['user']
        request.pecan['form'].process(obj=user)
        return dict(user=user)

    @index.when(method='POST', template='settings/profile.html')
    @with_form(UserProfileForm, error_cfg={'auto_insert_errors': True})
    def index_post(self, **kw):
        user = request.context['user']
        form = request.pecan['form']
        if form.errors:
            return dict(user=user, form=form)

        for k, v in kw.items():
            setattr(user, k, v)

        notify('Your settings have been saved.')
        redirect('/settings/profile', headers=response.headers)
