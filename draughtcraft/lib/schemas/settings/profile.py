from draughtcraft.lib.schemas.base  import FilteredSchema 
from formencode                     import validators


class UserProfileSchema(FilteredSchema):
    """
    This schema is for validating the fields saved for a user's profile
    """
    first_name      = validators.String()
    last_name       = validators.String()
    email           = validators.Email(not_empty=True)
