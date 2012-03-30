from pecan.ext.wtforms import (SecureForm, fields as f, validators as v,
                                ValidationError)
from draughtcraft import model


def email_exists(form, field):
    message = "Sorry, we couldn't find anyone with that email address."
    print field.data
    if model.User.get_by(email=field.data) is None:
        raise ValidationError(message)


class ForgotPasswordForm(SecureForm):

    email = f.TextField('Email Address', validators=[
        v.Required(),
        v.Email(),
        email_exists
    ])


class ResetPasswordForm(SecureForm):

    email = f.TextField('Email Address', validators=[
        v.Required(),
        v.Email()
    ])
    password = f.PasswordField('Password', validators=[
        v.Required(),
        v.Length(min=4),
        v.EqualTo('password_confirm', message='Passwords must match.')
    ])
    password_confirm = f.PasswordField('', validators=[
        v.Required(),
        v.Length(min=4),
        v.EqualTo('password', message='Passwords must match.')
    ])
