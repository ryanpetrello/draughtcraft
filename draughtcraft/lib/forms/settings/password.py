from pecan import request
from pecan.ext.wtforms import (SecureForm, fields as f, validators as v,
                               ValidationError)
from draughtcraft import model
from sqlalchemy import and_


def existing_matches(form, field):
    message = 'The provided password is not correct.'
    hashed = model.User.__hash_password__(field.data)

    if not model.User.query.filter(and_(
        model.User.username == request.context['user'].username,
        model.User.password == hashed
    )).count():
        raise ValidationError(message)


class UserPasswordForm(SecureForm):
    old_password = f.PasswordField('Existing Password', validators=[
        v.Required(),
        existing_matches
    ])
    password = f.PasswordField('New Password', validators=[
        v.Required(),
        v.Length(min=4),
        v.EqualTo('password_confirm', message='Passwords must match.')
    ])
    password_confirm = f.PasswordField('', validators=[
        v.Required(),
        v.Length(min=4),
        v.EqualTo('password', message='Passwords must match.')
    ])
