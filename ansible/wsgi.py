from pecan.deploy import deploy
app = deploy('/opt/web/draughtcraft/src/production.py')

from paste.exceptions.errormiddleware import ErrorMiddleware
app = ErrorMiddleware(
    app,
    error_email=app.conf.error_email,
    from_address=app.conf.error_email,
    smtp_server=app.conf.error_smtp_server,
    smtp_username=app.conf.error_email,
    smtp_password=app.conf.error_password,
    smtp_use_tls=True
)
