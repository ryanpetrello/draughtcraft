from draughtcraft.lib.schemas.base  import FilteredSchema 
from formencode                     import validators, All
from unique                         import UniqueUsername, UniqueEmail


class SignupSchema(FilteredSchema):
    """
    This schema is for validating a new signup.
    """
    username            = All(
                            UniqueUsername(not_empty=True),
                            validators.Regex(regex='^[a-zA-Z0-9_]{4,}$')
                          )
    password            = validators.String(not_empty=True)
    password_confirm    = validators.String(not_empty=True)
    email               = UniqueEmail(not_empty=True)

    chained_validators  = [
                            validators.FieldsMatch(
                                'password',
                                'password_confirm'
                            )
                          ]
