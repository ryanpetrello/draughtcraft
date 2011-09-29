from draughtcraft                   import model
from draughtcraft.tests             import TestModel
from draughtcraft.lib.schemas.base  import ModelObject
from formencode                     import Invalid


class TestModelObjectSchema(TestModel):

    def test_successful_model_lookup(self):
        model.User()
        model.commit()

        assert ModelObject(model.User).to_python(1) == model.User.get(1)

    def test_invalid_model_lookup(self):
        try:
            ModelObject(model.User).to_python(1)
        except Invalid: pass
        else: raise AssertionError('model.User.get(1) does not exist.')

    def test_invalid_model_lookup_alternative(self):
        assert ModelObject(model.User, if_invalid=None).to_python(1) == None

    def test_invalid_model_lookup_if_empty_value(self):
        model.User(username='ryanpetrello')
        model.commit()

        assert ModelObject(model.User, if_empty=1).to_python('') == model.User.get(1)

    def test_invalid_model_lookup_if_empty_filter(self):
        model.User(username='ryanpetrello')
        model.commit()

        assert ModelObject(model.User, if_empty=('username','ryanpetrello')).to_python('') == model.User.get(1)

    def test_model_lookup_with_filter(self):
        model.User(username='ryanpetrello')
        model.commit()

        assert ModelObject(model.User, filters={
            'username' : 'ryanpetrello'
        }).to_python(1) == model.User.get(1)

        assert ModelObject(model.User, if_invalid=None, filters={
            'username' : 'other'
        }).to_python(1) == None

    def test_model_lookup_with_lazy_filter(self):
        model.User(username='ryanpetrello')
        model.commit()

        assert ModelObject(model.User, filters={
            'username' : lambda: 'ryanpetrello'
        }).to_python(1) == model.User.get(1)

    def test_from_python(self):
        model.User(username='ryanpetrello')
        model.commit()

        assert ModelObject(model.User).from_python(model.User.get(1)) == 1
