from pecan.ext.wtforms import SecureForm
from pecan import request


def auth_token_pair():
    key = SecureForm.SECRET_KEY
    return (key, request.cookies.get(key))
