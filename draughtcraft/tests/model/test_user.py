from draughtcraft   import model
from hashlib        import sha256, md5

import unittest


class TestUser(unittest.TestCase):

    def test_full_name(self):
        assert model.User(
            first_name = 'Ryan', 
            last_name = 'Petrello'
        ).full_name == 'Ryan Petrello'

    def test_printed_name(self):
        assert model.User(
            first_name = 'Ryan', 
            last_name = 'Petrello',
            username = 'ryanpetrello'
        ).printed_name == 'Ryan Petrello'

        assert model.User(
            first_name = 'Ryan', 
            last_name = '',
            username = 'ryanpetrello'
        ).printed_name == 'Ryan'

        assert model.User(
            username = 'ryanpetrello'
        ).printed_name == 'ryanpetrello'

    def test_printed_first_name(self):
        assert model.User(
            first_name = 'Ryan', 
            last_name = 'Petrello',
            username = 'ryanpetrello'
        ).printed_first_name == 'Ryan'

        assert model.User(
            first_name = '', 
            last_name = 'Petrello',
            username = 'ryanpetrello'
        ).printed_first_name == 'ryanpetrello'

        assert model.User(
            username = 'ryanpetrello'
        ).printed_first_name == 'ryanpetrello'

    def test_abbreviated_name(self):
        assert model.User(
            first_name = 'Ryan', 
            last_name = 'Petrello',
            username = 'ryanpetrello'
        ).abbreviated_name == 'Ryan P.'

        assert model.User(
            first_name = 'Ryan', 
            last_name = '',
            username = 'ryanpetrello'
        ).abbreviated_name== 'ryanpetrello'

        assert model.User(
            username = 'ryanpetrello'
        ).abbreviated_name == 'ryanpetrello'

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
        assert user.gravatar == "http://www.gravatar.com/avatar/%s?d=404" % (
            md5('ryan@example.com').hexdigest()
        )

class TestUserSettings(unittest.TestCase):

    def test_default_creation(self):
        user = model.User(
            username    = u'ryanpetrello',
            password    = u'testing123',
            email       = u'ryan@example.com' 
        )
        assert user.settings['default_ibu_formula'] == 'tinseth'
        assert user.settings['default_recipe_volume'] == 5
        assert user.settings['default_recipe_type'] == 'MASH'
        assert user.settings['brewhouse_efficiency'] == .75

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
