from pecan                              import request
from draughtcraft                       import model
from draughtcraft.lib.notice            import notices
from webhelpers.html.tags               import *
from webhelpers.text                    import *
from draughtcraft.lib.csrf              import secure_form as form

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

def format_age(value):
    from datetime import datetime
    now = datetime.utcnow()

    difference = now - value
    
    # If it's been less than a day, return "minutes/hours ago"
    if difference.days == 0:
        minutes = int(round(difference.seconds / 60.0))
        if minutes >= 60:
            hours =  int(round(minutes / 60.0))
            if hours == 1: return '1 hour ago'
            return '%s hours ago' % hours
        elif minutes == 0:
            return 'just now'
        else:
            if minutes == 1: return '1 minute ago'
            return '%s minutes ago' % minutes
    elif isinstance(now, datetime) and isinstance(value, datetime):
        difference = now.date() - value.date()
        
    # Otherwise, print "Yesterday / X days ago"
    if difference.days == 1:
        return 'yesterday'
    elif difference.days >= 2 and difference.days <= 10:
        return '%s days ago' % difference.days
    else:
        return format_date(value)
