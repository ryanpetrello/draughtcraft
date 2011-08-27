from pecan                      import conf
from draughtcraft.lib           import email
from fudge.inspector            import arg

import os
import fudge
import unittest

def _gen_template_path():
    root = getattr(conf.app, 'modules', [])[0]
    return os.path.join(
        os.path.dirname(root.__file__),
        'tests',
        'fixtures',
        'emails'
    )
template_path = _gen_template_path()


class TestEmailTemplate(unittest.TestCase):

    def test_text_rendering(self):
        template = email.EmailTemplate('sample', template_path)
        body = template.text({'name': 'Ryan'})
        assert body == 'Hello, Ryan!'

    def test_text_rendering_with_missing_template(self):
        template = email.EmailTemplate('missing', template_path)
        assert template.text({'name': 'Ryan'}) == None

    def test_html_rendering(self):
        template = email.EmailTemplate('sample', template_path)
        body = template.html({'name': 'Ryan'})
        assert body == email.EmailTemplate.__html_wrap__ % '<p>Hello, Ryan!</p>'

    def test_html_rendering_with_missing_template(self):
        template = email.EmailTemplate('missing', template_path)
        assert template.html({'name': 'Ryan'}) == None


class TestEmailSend(unittest.TestCase):
    
    @fudge.patch('postmark.PMMail')
    def test_send(self, FakeMail):

        ns = {'username': 'sample_user'}

        (FakeMail.expects_call().with_args(
            api_key     = conf.postmark.api_key,
            to          = 'bob@example.com',
            cc          = 'bob+cc@example.com',
            bcc         = 'bob+bcc@example.com,ryan+bcc@example.com',
            subject     = 'Sample Subject',
            sender      = 'notify@draughtcraft.com',
            html_body   = email.EmailTemplate(
                            'signup', 
                            '%s/emails' % conf.app.template_path
                          ).html(ns),
            text_body   = email.EmailTemplate(
                            'signup', 
                            '%s/emails' % conf.app.template_path
                          ).text(ns)
        ).returns_fake().expects('send'))

        email.send(
            'bob@example.com',
            'signup',
            'Sample Subject',
            ns,
            cc = ['bob+cc@example.com'],
            bcc = ['bob+bcc@example.com', 'ryan+bcc@example.com']
        )
