from pecan                              import request
from draughtcraft                       import model
from draughtcraft.lib.notice            import notices
from webhelpers.html.tags               import *
from webhelpers.text                    import *
from draughtcraft.lib.csrf              import secure_form as form

#
# Resources, minification, and automatic resource file merging
#
def stamp(uri):
    """
    Used to stamp the URI of a static resource with a revision-specific
    identifier so that when updates are deployed, browser caches are broken,
    and users are forced to re-download the latest static resources.
    """
    from pecan import conf
    return "%s?%s" % (uri, conf.app.stamp)

def css(url):
    """
    Called from a template to add a CSS resource to the page.
    """
    if 'css_sources' not in request.context:
        request.context['css_sources'] = []
    request.context['css_sources'].append(url)
    return ''

def js(url):
    """
    Called from a template to add a JS resource to the page.
    """
    if 'js_sources' not in request.context:
        request.context['js_sources'] = []
    request.context['js_sources'].append(url)
    return ''

def compiled_css():
    """
    Returns the URL to an auto-merged CSS resource.

    If h.css() is called 3 times in a template, those 3 CSS files will
    be merged into a single file by h.compile_css(), stored in a Beaker
    memory cache, and the resulting <style> embedded into the template via
    this function."""
    from draughtcraft.lib.minify import stylesheet_link
    return stylesheet_link(
        *request.context.get('css_sources', []),
        combined = True
    )

def compiled_javascript():
    """
    Returns the URL to an auto-merged JS resource.

    If h.js() is called 3 times in a template, those 3 JS files will
    be merged into a single file by h.compile_javascript(), stored in a Beaker
    memory cache, and the resulting <script> embedded into the template via
    this function.
    """
    from draughtcraft.lib.minify import javascript_link
    return javascript_link(
        *request.context.get('js_sources', []),
        minified = True,
        combined = True
    )

#
# Various formatting helpers
#
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
