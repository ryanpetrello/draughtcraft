from draughtcraft   import model
from hashlib        import sha256


class TestUser(object):

    def test_password_conversion(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'ryan@example.com' 
        )

        correct = sha256('testing123' + 'example').hexdigest()
        assert user.password == correct

        user.password = 'tryagain'

        correct = sha256('tryagain' + 'example').hexdigest()
        assert user.password == correct
