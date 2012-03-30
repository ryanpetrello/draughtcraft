from pecan.ext.wtforms import (SecureForm, TextField, ValidationError,
                                validators as v)
from draughtcraft import model
from sqlalchemy import func


def unique(attr):
    message = "This %s is already in use.  Please choose another." % attr

    def taken_(form, field):
        if model.User.query.filter(
            func.lower(getattr(model.User, attr)) == field.data.lower()
        ).count() > 0:
            raise ValidationError(message)

    return taken_


class SignupForm(SecureForm):

    username = TextField('Username', validators=[
        v.Required(),
        v.Regexp(
            '^[a-zA-Z0-9_]{4,}$',
            message='Username must contain 4 or more letters or numbers.'
        ),
        unique('username')
    ])
    password = TextField('Password', validators=[
        v.Required(),
        v.Length(min=4),
        v.EqualTo('password_confirm', message='Passwords must match.')
    ])
    password_confirm = TextField('', validators=[
        v.Required(),
        v.Length(min=4),
        v.EqualTo('password', message='Passwords must match.')
    ])
    email = TextField('Email', validators=[
        v.Required(),
        v.Email(),
        unique('email')
    ])
