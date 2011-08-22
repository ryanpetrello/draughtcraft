from draughtcraft.lib.secure_form   import CrossRequestTokenValidator
from draughtcraft.lib.schemas.base  import FilteredSchema 
from formencode                     import validators, All
from unique                         import UniqueUsername, UniqueEmail


class SignupSchema(FilteredSchema):
    """
    This schema is for validating a new signup.
    """
    _form_authentication_token  = CrossRequestTokenValidator()
    username                    = All(
                                    UniqueUsername(not_empty=True),
                                    validators.Regex(regex='^[a-zA-Z0-9_]{4,}$')
                                )
    password                    = All(
                                    validators.String(not_empty=True),
                                    validators.Regex(
                                        regex='^.{4,}$',
                                        messages={
                                            'invalid': 'Passwords must be at least 4 characters in length.'
                                        }
                                    )
                                )
    password_confirm            = validators.String(not_empty=True)
    email                       = UniqueEmail(not_empty=True)

    chained_validators          = [
                                    validators.FieldsMatch(
                                        'password',
                                        'password_confirm'
                                    )
                                ]
