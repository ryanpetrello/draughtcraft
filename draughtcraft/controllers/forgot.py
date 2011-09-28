from pecan                              import (expose, request, response,
                                                redirect, ValidationException)
from pecan.rest                         import RestController
from draughtcraft                       import model
from draughtcraft.lib                   import email as emaillib
from draughtcraft.lib.notice            import notify
from draughtcraft.lib.schemas.forgot    import (ForgotPasswordSchema,
                                                ResetPasswordSchema)
from hashlib                            import sha256
from uuid                               import uuid1


class ResetController(RestController):
    
    @expose('forgot/reset.html')
    def get_one(self, code):
        
        req = model.PasswordResetRequest.get(code)
        if req is None:
            redirect('/forgot/missing', internal=True)
        
        return dict(password_request = req)
        
    @expose(
        schema          = ResetPasswordSchema(),
        htmlfill        = dict(auto_insert_errors = True, prefix_error = False),
        error_handler   = lambda: request.path        
    )
    def post(self, code, **kw):

        req = model.PasswordResetRequest.get(code)
        if req is None:
            redirect('/forgot/missing', internal=True)

        u = req.user
        if u.email != kw.get('email').strip():
            raise ValidationException(errors={
                "email": "Sorry, that email address is not valid."
            })

        # Delete the password request and change their password.
        req.delete()
        u.password = kw.get('password')
        
        notify("Your password has been reset.  Go ahead and log in.")
        return redirect('/login', headers=response.headers)

class ForgotPasswordController(object):
    
    @expose(generic=True)
    def index(self):
        pass # pragma: no cover
            
    @index.when(
        method              = 'POST',
        schema              = ForgotPasswordSchema(),
        htmlfill            = dict(auto_insert_errors = True, prefix_error = False),
        error_handler       = lambda: request.path
    )
    def do_post(self, email):
        
        u = model.User.get_by(email=email)
        if u is None:
            raise ValidationException(errors={
                "email": "Sorry, we couldn't find anyone with that email address."
            })
            
        # Generate a random hash
        code = sha256(str(uuid1())).hexdigest()

        # Store a password request for this user
        model.PasswordResetRequest(
            code    = code,
            user    = u
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
            
        notify("We've received your reset request.  You should receive an email with instructions shortly.")
        return redirect('/login', headers=response.headers)

    @index.when(method='GET', template='forgot/index.html')
    def do_get(self):
        return dict()
        
    @expose('forgot/missing.html')
    def missing(self):
        return dict()        
        
    reset = ResetController()
