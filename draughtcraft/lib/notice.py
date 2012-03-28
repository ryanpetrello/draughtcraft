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

    def pop_payload(self, request=None, response=None):
        """
        Fetches and decodes the flash payload from the request and sets the
        required Set-Cookie header in the response so the browser deletes the
        flash cookie.

        This method is intended to manage the flash payload without using
        JavaScript and requires webob compatible request/response
        objects.
        """
        # First try fetching it from the request
        request = request or self.get_request()
        response = response or self.get_response()
        if request is None or response is None:
            raise ValueError("Need to provide a request and reponse objects")
        payload = request.environ.get('webflash.payload', {})
        if not payload:
            payload = request.cookies.get(self.cookie_name, {})
            if payload:
                log.debug("Got payload from cookie")
        else:
            log.debug("Got payload for environ %d, %r",
                      id(request.environ), payload)
        if payload:
            payload = json.loads(unquote(payload))
            if 'webflash.deleted_cookie' not in request.environ:
                log.debug("Deleting flash payload")
                response.delete_cookie(self.cookie_name)
                request.environ['webflash.delete_cookie'] = True
        return payload or {}
    
notify = notices = Notify(
    cookie_name    = 'draughtcraft-notify',
    default_status = 'notice-general',
    get_response   = lambda: response,
    get_request    = lambda: request
)
