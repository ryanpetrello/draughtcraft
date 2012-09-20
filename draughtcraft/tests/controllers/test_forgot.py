from draughtcraft.tests import TestApp
from draughtcraft import model
from fudge.inspector import arg

import fudge


class TestForgotPassword(TestApp):

    def test_missing(self):
        assert self.get('/forgot/missing').status_int == 200

    def test_forgot_get(self):
        assert self.get('/forgot/').status_int == 200

    def test_password_reset_empty_email(self):
        self.post('/forgot/', params={
            'email': ''
        })
        assert model.PasswordResetRequest.query.count() == 0

    def test_password_reset_invalid_email_format(self):
        self.post('/forgot/', params={
            'email': 'ryan@example'
        })
        assert model.PasswordResetRequest.query.count() == 0

    def test_password_reset_unrecognized_email(self):
        response = self.post('/forgot/', params={
            'email': 'ryan@example.com'
        })

        assert "Sorry, we couldn't find anyone with that email address." in \
            response.body
        assert model.PasswordResetRequest.query.count() == 0

    @fudge.patch('draughtcraft.lib.email.send')
    def test_password_reset(self, fake_send):
        (fake_send.expects_call().with_args(
            'ryan@example.com',
            'forgot',
            'Reset Your Draughtcraft Password',
            {'name': 'Ryan', 'code': arg.any()}
        ))

        model.User(first_name=u'Ryan', email=u'ryan@example.com')
        model.commit()

        response = self.post('/forgot/', params={
            'email': model.User.get(1).email
        })

        assert model.PasswordResetRequest.query.count() == 1

        assert response.status_int == 302
        assert response.headers['Location'].endswith('/login')

    def test_password_reset_lookup(self):
        response = self.get('/forgot/reset/ABC123')
        assert 'This reset password page has expired' in response.body

    def test_choose_new_password(self):
        model.User(
            username='ryan',
            first_name=u'Ryan',
            email=u'ryan@example.com'
        )
        model.commit()

        model.PasswordResetRequest(
            code='ABC123',
            user=model.User.get(1)
        )

        response = self.post('/forgot/reset/ABC123', params={
            'email': 'ryan@example.com',
            'password': 'newpass',
            'password_confirm': 'newpass'
        })

        assert response.status_int == 302
        assert response.headers['Location'].endswith('/login')

        assert model.PasswordResetRequest.query.count() == 0
        assert model.User.validate(
            'ryan',
            'newpass'
        ) == model.User.query.first()

    def test_choose_new_password_expired(self):
        model.User(
            username='ryan',
            password='testing',
            first_name=u'Ryan',
            email=u'ryan@example.com'
        )
        model.commit()

        response = self.post('/forgot/reset/ABC123', params={
            'email': 'ryan@example.com',
            'password': 'newpass',
            'password_confirm': 'newpass'
        })

        assert response.status_int == 200

        assert model.PasswordResetRequest.query.count() == 0
        assert model.User.validate(
            'ryan',
            'newpass'
        ) is None
        assert model.User.validate(
            'ryan',
            'testing'
        ) == model.User.query.first()

    def test_choose_new_password_invalid_email(self):
        model.User(
            username='ryan',
            password='testing',
            first_name=u'Ryan',
            email=u'ryan@example.com'
        )
        model.commit()

        model.PasswordResetRequest(
            code='ABC123',
            user=model.User.get(1)
        )

        self.post('/forgot/reset/ABC123', params={
            'email': 'invalid@example.com',
            'password': 'newpass',
            'password_confirm': 'newpass'
        })

        assert model.PasswordResetRequest.query.count() == 1
        assert model.User.validate(
            'ryan',
            'newpass'
        ) is None
        assert model.User.validate(
            'ryan',
            'testing'
        ) == model.User.query.first()

    def test_choose_new_password_mismatch(self):
        model.User(
            username='ryan',
            password='testing',
            first_name=u'Ryan',
            email=u'ryan@example.com'
        )
        model.commit()

        model.PasswordResetRequest(
            code='ABC123',
            user=model.User.get(1)
        )

        self.post('/forgot/reset/ABC123', params={
            'email': 'ryan@example.com',
            'password': 'newpass',
            'password_confirm': 'invalid'
        })

        assert model.PasswordResetRequest.query.count() == 1
        assert model.User.validate(
            'ryan',
            'newpass'
        ) is None
        assert model.User.validate(
            'ryan',
            'testing'
        ) == model.User.query.first()
