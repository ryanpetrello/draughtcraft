from pecan                              import request
from draughtcraft                       import model
from draughtcraft.lib.notice            import notices
from webhelpers.html.tags               import *
from draughtcraft.lib.secure_form       import secure_form as form

def format_percentage(decimal, digits=2, symbol=True):
    value = decimal * 100.00

    # Use string formatting to format at X digits
    p = ''.join((u'%.',str(digits),'f')) % value

    # Remove padded zeroes
    while p.endswith('0'):
        p = p[:-1]

    # Remove trailing decimal points
    if p.endswith('.'):
        p = p[:-1]      

    # Apply an % symbol
    if symbol:
        return '%s%%' % p

    return p

def format_date(value, format='%b %d, %Y'):
    if not value:
        value = date.today()
    return value.strftime(format).replace(' 0', ' ')
