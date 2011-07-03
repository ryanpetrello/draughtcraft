from pecan          import request
from pecan.secure   import SecureController
from profile        import ProfileController


class SettingsController(SecureController):

    @classmethod
    def check_permissions(cls):
        return request.context['user'] is not None

    profile = ProfileController()
