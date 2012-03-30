from pecan import expose, request, response, redirect
from pecan.rest import RestController
from pecan.ext.wtforms import with_form, redirect_to_handler
from draughtcraft import model
from draughtcraft.lib import email as emaillib
from draughtcraft.lib.notice import notify
from draughtcraft.lib.forms.forgot import ForgotPasswordForm, ResetPasswordForm
from hashlib import sha256
from uuid import uuid1


class ResetController(RestController):

    @expose('forgot/reset.html')
    @with_form(ResetPasswordForm)
    def get_one(self, code):

        req = model.PasswordResetRequest.get(code)
        if req is None:
            redirect('/forgot/missing', internal=True)

        return dict(password_request=req)

    @expose()
    @with_form(ResetPasswordForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def post(self, code, **kw):
        req = model.PasswordResetRequest.get(code)
        if req is None:
            redirect('/forgot/missing', internal=True)

        u = req.user
        if u.email != kw.get('email').strip():
            form = request.pecan['form']
            form.email.errors.append(
                "Sorry, that email address is not valid."
            )
            redirect_to_handler(form, request.path)

        # Delete the password request and change their password.
        req.delete()
        u.password = kw.get('password')

        notify("Your password has been reset.  Go ahead and log in.")
        return redirect('/login', headers=response.headers)


class ForgotPasswordController(object):

    @expose(generic=True, template='forgot/index.html')
    @with_form(ForgotPasswordForm)
    def index(self):
        return dict()

    @index.when(method='POST')
    @with_form(ForgotPasswordForm, error_cfg={
        'auto_insert_errors': True,
        'handler': lambda: request.path
    })
    def do_post(self, email):
        # Generate a random hash
        code = sha256(str(uuid1())).hexdigest()

        u = model.User.get_by(email=email)
        assert u is not None

        # Store a password request for this user
        model.PasswordResetRequest(
            code=code,
            user=u
        )

        # Generate the email
        emaillib.send(
            u.email,
            'forgot',
            'Reset Your Draughtcraft Password',
            {
                'name': u.printed_name,
                'code': code
            }
        )

        notify(("We've received your reset request.  You should receive an "
                "email with instructions shortly."))
        return redirect('/login', headers=response.headers)

    @expose('forgot/missing.html')
    def missing(self):
        return dict()

    reset = ResetController()
