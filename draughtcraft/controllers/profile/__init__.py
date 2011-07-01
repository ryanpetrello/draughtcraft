from pecan          import expose, abort
from draughtcraft   import model


class ProfileController(object):

    def __init__(self, username):
        self.user = model.User.get_by(username=username)
        if self.user is None:
            abort(404)

    @expose('profile/index.html')
    def index(self):
        return dict(user = self.user)


class ProfilesController(object):

    @expose()
    def _lookup(self, username, *remainder):
        return ProfileController(username), remainder
