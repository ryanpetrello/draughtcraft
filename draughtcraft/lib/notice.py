"""
Messaging system for displaying messages to users on
redirects.
"""
from pecan import request, response
from random import randint
from urllib import quote, unquote
import simplejson

__all__ = ['notify', 'notices']


class Notify(object):

    static_template = '<div class="ribbon %(status)s">%(message)s</div>'

    def __init__(self, cookie_name, get_request, get_response,
                    default_status='ok'):
        self.cookie_name = cookie_name
        self.default_status = default_status
        self.get_request = get_request
        self.get_response = get_response

    def __call__(self, message, status=None, **extra_payload):

        # append the "notify-" prefix to the status
        if status and not status.startswith('notice-'):
            status = 'notice-%s' % status

        payload = self.prepare_payload(
            message=message,
            status=status or self.default_status,
            **extra_payload
        )

        self.get_request().environ['dcflash.payload'] = payload
        self.get_response().set_cookie(self.cookie_name, payload)

        # make sure the cookie length won't be exceeded
        if len(self.get_response().headers['Set-Cookie']) > 4096:
            raise ValueError(
                'Notification value is too long (cookie would be >4k)'
            )

    def prepare_payload(self, **data):
        return quote(simplejson.dumps(data))

    def pop_payload(self):
        payload = self.get_request().environ.get('dcflash.payload', {}) or \
                    self.get_request().cookies.get(self.cookie_name, {})
        if payload:
            payload = simplejson.loads(unquote(payload))
            if 'dcflash.deleted_cookie' not in self.get_request().environ:
                self.get_response().delete_cookie(self.cookie_name)
                self.get_request().environ['dcflash.delete_cookie'] = True
        return payload or {}

    def render(self):
        payload = self.pop_payload()
        if not payload:
            return ''
        payload['message'] = html_escape(payload.get('message', ''))
        payload['container_id'] = 'notify-%s' % randint(1000, 9999)
        return self.static_template % payload

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c, c) for c in text)

notify = notices = Notify(
    cookie_name='draughtcraft-notify',
    default_status='notice-general',
    get_request=lambda: request,
    get_response=lambda: response
)
