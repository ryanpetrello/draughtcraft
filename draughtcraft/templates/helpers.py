from pecan                      import request
from draughtcraft               import model
from webhelpers.html.tags       import *

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
