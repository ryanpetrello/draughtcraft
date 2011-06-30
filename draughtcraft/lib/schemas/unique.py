from formencode     import validators, Invalid
from draughtcraft   import model
from sqlalchemy     import func


class UniqueUsername(validators.FancyValidator):

    messages = {
        'not_unique': 'This username is unavailable.  Please choose another.'
    }
    
    def __init__(self, **kw):
        super(UniqueUsername, self).__init__(**kw)
    
    def _to_python(self, value, state):
        return value.strip()
    
    def validate_python(self, value, state):
        taken = model.User.query.filter(
            model.User.username == value.lower()
        ).count() > 0

        if taken:
            raise Invalid(self.message("not_unique", state), value, state)
        
class UniqueEmail(validators.Email):

    messages = {
        'not_unique': 'This email address is already associated with another account.  Please choose another.'
    }
    
    def __init__(self, exclude_existing_user=True, **kw):
        super(UniqueEmail, self).__init__(**kw)        
    
    def _to_python(self, value, state):
        return value.strip()    

    def validate_python(self, value, state):
        super(UniqueEmail, self).validate_python(value, state)
        
        taken = model.User.query.filter(
            func.lower(model.User.email) == value.lower()
        ).count() > 0
        
        if taken:
            raise Invalid(self.message("not_unique", state), value, state)
