from draughtcraft                   import model
from draughtcraft.lib.schemas.base  import FilteredSchema 
from formencode                     import validators, Invalid
from sqlalchemy                     import and_


class ValidUsernameAndPassword(validators.FormValidator):

    show_match = False
    field_names = None
    validate_partial_form = True

    __unpackargs__ = ('*', 'field_names')

    messages = dict(
        invalid = 'The provided username and password are not valid'
    )

    def __init__(self, *args, **kw):
        super(ValidUsernameAndPassword, self).__init__(*args, **kw)

    def validate_partial(self, field_dict, state):
            for name in self.field_names:
                if name not in field_dict:
                    return
            self.validate_python(field_dict, state)
    
    def validate_python(self, field_dict, state):

        username, password = field_dict['username'], field_dict['password']

        hashed = model.User.__hash_password__(password)

        if not model.User.query.filter(and_(
            model.User.username == username,
            model.User.password == hashed
        )).count():

            error = 'The provided username and password are not valid', 
            raise Invalid(
                error,
                field_dict, 
                state,
                error_dict = {
                    'username'  : self.message('invalid', state),
                    'password'  : self.message('invalid', state)
                }
            )


class LoginSchema(FilteredSchema):
    """
    This schema is for validating login username/password values.
    """
    username            = validators.String(not_empty=True)
    password            = validators.String(not_empty=True)

    chained_validators  = [ValidUsernameAndPassword(
                            'username',
                            'password'
                          )]
