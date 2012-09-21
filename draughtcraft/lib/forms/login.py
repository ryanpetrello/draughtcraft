from pecan.ext.wtforms import SecureForm, TextField, PasswordField, Required
from draughtcraft import model


class LoginForm(SecureForm):

    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])

    def validate(self):
        # regular validation
        if not super(LoginForm, self).validate():
            return False

        if model.User.validate(self.username.data, self.password.data) is None:
            self.username.errors.append(
                'The provided username and password are not valid.'
            )
            self.password.errors.append(
                'The provided username and password are not valid.'
            )
            return False

        return True
