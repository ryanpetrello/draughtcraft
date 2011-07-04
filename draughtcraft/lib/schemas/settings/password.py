from draughtcraft.lib.schemas.base  import FilteredSchema 
from formencode                     import validators


class UserPasswordSchema(FilteredSchema):
    """
    This schema is for validating password changes.
    """
    old_password        = validators.String()
    password            = validators.String()
    password_confirm    = validators.String()
