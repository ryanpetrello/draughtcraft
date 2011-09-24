from elixir                             import (Entity, Field, Unicode, DateTime,
                                                Enum, UnicodeText, OneToMany,
                                                ManyToOne)
from draughtcraft.model.deepcopy        import ShallowCopyMixin
from pecan                              import conf
from simplejson                         import loads, dumps
from datetime                           import datetime
from hashlib                            import sha256, md5
from sqlalchemy.ext.associationproxy    import AssociationProxy
from sqlalchemy.orm.collections         import attribute_mapped_collection


class User(Entity, ShallowCopyMixin):

    first_name      = Field(Unicode(64), index=True)
    last_name       = Field(Unicode(64), index=True)

    username        = Field(Unicode(64), unique=True, index=True)
    _password       = Field(Unicode(64), colname='password', synonym='password')
    email           = Field(Unicode(64), index=True)
    bio             = Field(Unicode(512))
    signup_date     = Field(DateTime, default=datetime.utcnow)

    location        = Field(Unicode(256))

    unit_system     = Field(Enum('US', 'METRIC'), default='US')

    recipes         = OneToMany('Recipe', inverse='author', order_by='-last_updated')
    user_settings   = OneToMany('UserSetting', cascade='all, delete-orphan',
                                   collection_class=attribute_mapped_collection('name'))
    settings        = AssociationProxy('user_settings', 'value', 
                                          creator=lambda name, value: UserSetting(name=name, value=value))

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        UserSetting.init_defaults(self)

    @property
    def full_name(self):
        return "%s %s" % (
            self.first_name or '',
            self.last_name or ''
        )

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, v):
        self._password = self.__hash_password__(v)

    @property
    def published_recipes(self):
        return filter(lambda r: r.state == "PUBLISHED", self.recipes)

    @property
    def drafts(self):
        return filter(lambda r: r.state == "DRAFT" and r.published_version is None, self.recipes)

    @property
    def gravatar(self):
        return 'http://www.gravatar.com/avatar/%s?d=404' % (
            md5(self.email.strip().lower()).hexdigest()
        )

    @classmethod
    def __hash_password__(self, v):
        salt = getattr(
            getattr(conf, 'session', None), 
            'password_salt', 
            'example'
        )
        return sha256(v + salt).hexdigest()


class UserSetting(Entity):
    user        = ManyToOne('User')
    name        = Field(Unicode(64), index=True)
    _value      = Field(UnicodeText)

    __defaults__ = {
        'default_ibu_formula'   : 'tinseth',
        'default_recipe_volume' : 5,
        'default_recipe_type'   : 'MASH',
        'brewhouse_efficiency'  : .75
    }

    @classmethod
    def init_defaults(cls, user):
        defaults = UserSetting.__defaults__.items()
        for n, v in defaults:
            cls(user=user, name=n, value=v)

    """
    Encode the actual value as JSON so we can retain its data type.
    """
    @property
    def value(self):
        return loads(self._value)

    @value.setter
    def value(self, v):
        self._value = dumps(v)


class PasswordResetRequest(Entity):
    code            = Field(Unicode(64), primary_key=True)
    datetime        = Field(DateTime)
    
    user            = ManyToOne('User')
