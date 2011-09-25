import random

from pecan                      import request, abort
from pecan.hooks                import PecanHook
from formencode                 import Invalid
from formencode.validators      import FancyValidator
from webhelpers.html.builder    import HTML, literal
from webhelpers.html.tags       import form as insecure_form
from webhelpers.html.tags       import hidden

import urlparse

"""
Secure Form Tag Helpers -- For prevention of Cross-site request forgery (CSRF)
attacks.

Generates form tags that include client-specific authorization tokens to be
verified by the destined web app.

Heavily influenced by webhelpers.pylonslib.secure_form
https://bitbucket.org/bbangert/webhelpers/src
"""

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

def auth_token_pair():
    return (token_key, authentication_token())

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


class CSRFPreventionHook(PecanHook):
    """
    Hook that requires a valid CSRF request token for any request not deemed safe'
    by RFC2616.
    """

    def same_origin(self, url1, url2):
        """
        Checks if two URLs are 'same-origin'
        """
        p1, p2 = urlparse.urlparse(url1), urlparse.urlparse(url2)
        return (p1.scheme, p1.hostname, p1.port) == (p2.scheme, p2.hostname, p2.port)
    
    def on_route(self, state):
        request = state.request

        # For simplicity, don't require CSRF for unit tests.
        if request.environ.get('paste.testing'): return

        if request.method not in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            referer = request.headers.get('Referer')

            # If there is no specified referer...
            if referer is None:
                abort(403, empty_body=True)

            #
            # If the hostname of the referer and the requested resource
            # don't match...
            #
            origin = 'http://%s/' % request.host
            if not self.same_origin(referer, origin):
                abort(403, empty_body=True)

            # If a CSRF token isn't available in the session
            token = authentication_token()
            if token is None:
                abort(403, empty_body=True)

            #
            # If the CSRF token in the session doesn't match the value
            # included in the request...
            #
            if token != request.params.get(token_key):
                abort(403, empty_body=True)
