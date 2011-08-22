from pecan                      import conf
from draughtcraft.lib.email     import EmailTemplate, send

import py
import py.test

import os


class TestEmailTemplate(object):

    @property
    def template_path(self):
        root = getattr(conf.app, 'modules', [])[0]
        return os.path.join(
            os.path.dirname(root.__file__),
            'tests',
            'fixtures',
            'emails'
        )

    def test_text_rendering(self):
        template = EmailTemplate('sample', self.template_path)
        body = template.text({'name': 'Ryan'})
        assert body == 'Hello, Ryan!'

    def test_text_rendering_with_missing_template(self):
        template = EmailTemplate('missing', self.template_path)
        assert template.text({'name': 'Ryan'}) == None

    def test_html_rendering(self):
        template = EmailTemplate('sample', self.template_path)
        body = template.html({'name': 'Ryan'})
        assert body == EmailTemplate.__html_wrap__ % '<p>Hello, Ryan!</p>'

    def test_html_rendering_with_missing_template(self):
        template = EmailTemplate('missing', self.template_path)
        assert template.html({'name': 'Ryan'}) == None
