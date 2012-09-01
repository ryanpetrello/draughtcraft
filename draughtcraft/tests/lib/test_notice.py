from unittest                       import TestCase
from webob                          import Request, Response
from json                           import dumps
from draughtcraft.lib.notice        import Notify

import pecan


class TestNotice(TestCase):

    def test_notify_render(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.request.environ['dcflash.payload'] = dumps({
            'message': 'It worked!',
            'status': 'notify-general'
        })
        assert '<div class="ribbon notify-general">It worked!</div>' == Notify(
            'cookie-name',
            default_status='general',
            get_response=lambda: Response(),
            get_request=lambda: pecan.core.state.request
        ).render()

    def test_notice_save(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.response = Response()

        n = Notify(
            'cookie-name',
            default_status='general',
            get_response=lambda: pecan.core.state.response,
            get_request=lambda: pecan.core.state.request
        )
        n('It worked!', 'general')

        assert n.render() == \
                '<div class="ribbon notice-general">It worked!</div>'

    def test_save_over_4k_cookie(self):
        pecan.core.state.request = Request.blank('/')
        pecan.core.state.response = Response()

        n = Notify(
            'cookie-name',
            default_status='general',
            get_response=lambda: pecan.core.state.response,
            get_request=lambda: pecan.core.state.request
        )

        try:
            n('X' * 4097, 'general')
        except ValueError, e:
            assert 'value is too long' in e.message
        else:
            assert AssertionError('Cookie size should be restricted to <= 4K')
