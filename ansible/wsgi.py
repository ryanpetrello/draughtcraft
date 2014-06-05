from pecan import conf
from pecan.deploy import deploy
app = deploy('/opt/web/draughtcraft/src/production.py')

from paste.exceptions.errormiddleware import ErrorMiddleware
app = ErrorMiddleware(
    app,
    error_email=conf.error_email,
    from_address=conf.error_email,
    smtp_server=conf.error_smtp_server,
    smtp_username=conf.error_email,
    smtp_password=conf.error_password,
    smtp_use_tls=True
)
