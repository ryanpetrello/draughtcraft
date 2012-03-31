from pecan.ext.wtforms import (SecureForm, fields as f, validators as v,
                                widgets as w)
from cgi import escape


class CustomTextArea(object):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        value = unicode(field._value())
        if 'value' in kwargs and kwargs['value']:
            value = kwargs['value']
        return w.HTMLString(u'<textarea %s>%s</textarea>' % (
            w.html_params(name=field.name, **kwargs),
            escape(value)
        ))


class UserProfileForm(SecureForm):
    first_name = f.TextField('')
    last_name = f.TextField('')
    email = f.TextField('Email', validators=[
        v.Required(),
        v.Email()
    ])
    location = f.TextField('Location')
    bio = f.TextAreaField('Bio', widget=CustomTextArea(), validators=[
        v.Length(max=512)
    ])
