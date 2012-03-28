from pecan.ext.wtforms import SecureForm, TextField, PasswordField, Required


class LoginForm(SecureForm):

    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
