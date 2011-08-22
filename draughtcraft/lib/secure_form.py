"""
Secure Form Tag Helpers -- For prevention of Cross-site request forgery (CSRF)
attacks.

Generates form tags that include client-specific authorization tokens to be
verified by the destined web app.

Heavily influenced by webhelpers.pylonslib.secure_form
https://bitbucket.org/bbangert/webhelpers/src
"""

import random

from pecan                      import request
from formencode                 import Invalid
from formencode.validators      import FancyValidator
from webhelpers.html.builder    import HTML, literal
from webhelpers.html.tags       import form as insecure_form
from webhelpers.html.tags       import hidden

token_key = "_form_authentication_token"

def authentication_token():
    """Return the current authentication token, creating one if one doesn't
    already exist.
    """
    session = request.environ['beaker.session']
    if not token_key in session:
        try:
            token = str(random.getrandbits(128))
        except AttributeError: # Python < 2.4
            token = str(random.randrange(2**128))
        session[token_key] = token
        session.save()
    return session[token_key]

def auth_token_hidden_field():
    token = hidden(token_key, authentication_token())
    return HTML.div(token, style="display: none;")

def secure_form(url, method="POST", multipart=False, **attrs):
    """Start a form tag that points the action to an url. This
    form tag will also include the hidden field containing
    the auth token.

    The url options should be given either as a string, or as a 
    ``url()`` function. The method for the form defaults to POST.

    Options:

    ``multipart``
        If set to True, the enctype is set to "multipart/form-data".
    ``method``
        The method to use when submitting the form, usually either 
        "GET" or "POST". If "PUT", "DELETE", or another verb is used, a
        hidden input with name _method is added to simulate the verb
        over POST.

    """
    form = insecure_form(url, method, multipart, **attrs)
    token = auth_token_hidden_field()
    return literal("%s\n%s" % (form, token))


class CrossRequestTokenValidator(FancyValidator):

    _ = lambda s: s

    messages = dict(
        invalid = _('The provided cross request form token is invalid.')
    )

    def validate_python(self, value, state):
        if value != authentication_token():
            raise Invalid(self.message('invalid', state), value, state)

    def _to_python(self, value, state):
        return value
