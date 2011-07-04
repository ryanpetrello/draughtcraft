from pecan          import request
from pecan.secure   import SecureController
from password       import PasswordController
from profile        import ProfileController


class SettingsController(SecureController):

    @classmethod
    def check_permissions(cls):
        return request.context['user'] is not None

    password    = PasswordController()
    profile     = ProfileController()
