from draughtcraft   import model
from hashlib        import sha256, md5


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

    def test_gravatar(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'  RYAN@example.COM  ' 
        )
        assert user.gravatar == "http://www.gravatar.com/avatar/%s?d=mm" % (
            md5('ryan@example.com').hexdigest()
        )

class TestUserSettings(object):

    def test_default_creation(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'ryan@example.com' 
        )
        assert user.settings['default_ibu_formula'] == 'tinseth'
        assert user.settings['default_recipe_volume'] == 5
        assert user.settings['default_recipe_type'] == 'MASH'

    def test_json_value(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'ryan@example.com' 
        )
        assert user.user_settings['default_ibu_formula']._value == '"tinseth"'
        assert user.user_settings['default_recipe_volume']._value == '5'

    def test_setting_change(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'ryan@example.com' 
        )
        user.settings['default_ibu_formula'] = 'rager'

        assert user.user_settings['default_ibu_formula']._value == '"rager"'

    def test_setting_add(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'ryan@example.com' 
        )
        user.settings['example'] = 5.5

        assert user.user_settings['example']._value == '5.5'
