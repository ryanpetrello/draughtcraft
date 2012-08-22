from pecan import conf
from draughtcraft.tests import TestModel
from draughtcraft.lib import email

import os
import fudge
import unittest


def _gen_template_path():
    return os.path.join(
        os.path.dirname(__file__),
        '..',
        'fixtures',
        'emails'
    )


class TestEmailTemplate(unittest.TestCase):

    @property
    def template_path(self):
        return _gen_template_path()

    def test_text_rendering(self):
        template = email.EmailTemplate('sample', self.template_path)
        body = template.text({'name': 'Ryan'})
        assert body == 'Hello, Ryan!'

    def test_text_rendering_with_missing_template(self):
        template = email.EmailTemplate('missing', self.template_path)
        assert template.text({'name': 'Ryan'}) == None

    def test_html_rendering(self):
        template = email.EmailTemplate('sample', self.template_path)
        body = template.html({'name': 'Joe'})
        assert body == email.EmailTemplate.__html_wrap__ % '<p>Hello, Joe!</p>'

    def test_html_rendering_with_missing_template(self):
        template = email.EmailTemplate('missing', self.template_path)
        assert template.html({'name': 'Ryan'}) == None


class TestEmailSend(TestModel):

    @fudge.patch('postmark.PMMail')
    def test_send(self, FakeMail):

        ns = {'username': 'sample_user'}

        (FakeMail.expects_call().with_args(
            api_key=conf.postmark.api_key,
            to='bob@example.com',
            cc='bob+cc@example.com',
            bcc='bob+bcc@example.com,ryan+bcc@example.com',
            subject='Sample Subject',
            sender='notify@draughtcraft.com',
            html_body=email.EmailTemplate(
                            'signup',
                            '%s/emails' % conf.app.template_path
                          ).html(ns),
            text_body=email.EmailTemplate(
                            'signup',
                            '%s/emails' % conf.app.template_path
                          ).text(ns)
        ).returns_fake().expects('send'))

        email.send(
            'bob@example.com',
            'signup',
            'Sample Subject',
            ns,
            cc=['bob+cc@example.com'],
            bcc=['bob+bcc@example.com', 'ryan+bcc@example.com']
        )
