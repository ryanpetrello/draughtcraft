from pecan.ext.wtforms import SecureForm, TextField, PasswordField, Required
from draughtcraft import model
from sqlalchemy import and_


class LoginForm(SecureForm):

    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])

    def validate(self):
        # regular validation
        if not super(LoginForm, self).validate():
            return False

        username, password = self.username.data, self.password.data
        hashed = model.User.__hash_password__(password)

        if not model.User.query.filter(and_(
            model.User.username == username,
            model.User.password == hashed
        )).count():
            self.username.errors.append(
                'The provided username and password are not valid.'
            )
            self.password.errors.append(
                'The provided username and password are not valid.'
            )
            return False

        return True
