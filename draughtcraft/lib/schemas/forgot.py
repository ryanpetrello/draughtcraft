from formencode                     import validators as v, All
from draughtcraft.lib.schemas.base  import FilteredSchema 

class ForgotPasswordSchema(FilteredSchema):
    
    email    = v.Email(not_empty=True)
    
class ResetPasswordSchema(FilteredSchema):

    email               = v.Email(not_empty=True)
    password            = All(
                            v.String(not_empty=True),
                            v.Regex(
                                regex='^.{4,}$',
                                messages={
                                    'invalid': 'Passwords must be at least 4 characters in length.'
                                }
                            )
                          )
    password_confirm    = v.String(not_empty=True)

    chained_validators  = [v.FieldsMatch(
                                'password',
                                'password_confirm'
                            )]
