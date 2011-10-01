from pecan                              import request
from draughtcraft                       import model
from draughtcraft.lib.notice            import notices
from webhelpers.html.tags               import *
from webhelpers.text                    import *
from draughtcraft.lib.csrf              import secure_form as form

def css(url):
    if 'css_sources' not in request.context:
        request.context['css_sources'] = []
    request.context['css_sources'].append(url)
    return ''

def js(url):
    if 'js_sources' not in request.context:
        request.context['js_sources'] = []
    request.context['js_sources'].append(url)
    return ''

def compiled_css():
    from draughtcraft.lib.minify import stylesheet_link
    return stylesheet_link(
        *request.context.get('css_sources', []),
        combined = True
    )

def compiled_javascript():
    from draughtcraft.lib.minify import javascript_link
    return javascript_link(
        *request.context.get('js_sources', []),
        minified = True,
        combined = True
    )

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

def format_volume(amount):
    amount = round(amount, 2)
    if float(amount) == int(amount):
        return int(amount)
    return amount

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    import re
    def tryint(s):
        try:
            return int(s)
        except:
            return s
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]
