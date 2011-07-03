"""
Messaging system for displaying messages to users on 
redirects.
"""
from pecan    import request, response
from random   import randint
from webflash import Flash


__all__ = ['notify', 'notices']


class Notify(Flash):
    
    static_template = '<div class="ribbon %(status)s">%(message)s</div>'
    
    def __call__(self, message, status=None, **extra_payload):
        
        # append the "notify-" prefix to the status
        if status and not status.startswith('notice-'):
            status = 'notice-%s' % status
        
        # force the message to be unicode so lazystrings, etc... are coerced
        result = super(Notify, self).__call__(
            unicode(message), status, **extra_payload
        )
        
        # make sure the cookie length won't be exceeded
        if len(response.headers['Set-Cookie']) > 4096:
            raise ValueError, 'Notification value is too long (cookie would be >4k)'
        
        return result

    def render(self, request=None, response=None):
        container_id = 'notify-%s' % randint(1000, 9999)
        return super(Notify, self).render(container_id, 
                                         use_js=False,
                                         request=request, 
                                         response=response)
    
    def _render_static_version(self, container_id, request, response):
        payload = self.pop_payload(request, response)
        if not payload:
            return ''
        payload['message'] = payload.get('message','')
        payload['container_id'] = container_id
        return self.static_template % payload


notify = notices = Notify(
    cookie_name    = 'draughtcraft-notify',
    default_status = 'notice-general',
    get_response   = lambda: response,
    get_request    = lambda: request
)
