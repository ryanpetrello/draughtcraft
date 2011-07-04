from pecan                          import request
from draughtcraft                   import model
from draughtcraft.lib.schemas.base  import FilteredSchema 
from sqlalchemy                     import and_
from formencode                     import validators, All, Invalid


class ValidPassword(validators.FormValidator):

    show_match = False
    field_names = None
    validate_partial_form = True

    __unpackargs__ = ('*', 'field_names')

    messages = dict(
        invalid = 'The provided password is not correct'
    )

    def __init__(self, *args, **kw):
        super(ValidPassword, self).__init__(*args, **kw)

    def validate_partial(self, field_dict, state):
            for name in self.field_names:
                if name not in field_dict:
                    return
            self.validate_python(field_dict, state)
    
    def validate_python(self, field_dict, state):

        password = field_dict['old_password']

        hashed = model.User.__hash_password__(password)

        if not model.User.query.filter(and_(
            model.User.username == request.context['user'].username,
            model.User.password == hashed
        )).count():

            error = 'The provided password is not correct', 
            raise Invalid(
                error,
                field_dict, 
                state,
                error_dict = {
                    'old_password'  : self.message('invalid', state)
                }
            )


class UserPasswordSchema(FilteredSchema):
    """
    This schema is for validating password changes.
    """
    old_password        = validators.String(not_empty=True)
    password            = All(
                            validators.String(not_empty=True),
                            validators.Regex(
                                regex='^.{4,}$',
                                messages={
                                    'invalid': 'Passwords must be at least 4 characters in length.'
                                }
                            )
                          )
    password_confirm    = validators.String(not_empty=True)

    chained_validators  = [
                            ValidPassword(
                                'old_password'
                            ),
                            validators.FieldsMatch(
                                'password',
                                'password_confirm'
                            )
                          ]
