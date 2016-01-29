from json import loads, dumps
from datetime import datetime
from hashlib import sha256, md5
from base64 import b64encode
from os import urandom

from elixir import (
    Entity, Field, Unicode, DateTime,
    UnicodeText, OneToMany, ManyToOne
)
from pecan import conf
from pbkdf2 import PBKDF2
from sqlalchemy import and_
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from draughtcraft.model.deepcopy import ShallowCopyMixin


class User(Entity, ShallowCopyMixin):

    first_name = Field(Unicode(64), index=True)
    last_name = Field(Unicode(64), index=True)

    username = Field(Unicode(64), unique=True, index=True)
    _password = Field(
        Unicode(64), colname='password', synonym='password')
    email = Field(Unicode(64), index=True)
    bio = Field(Unicode(512))
    signup_date = Field(DateTime, default=datetime.utcnow)

    location = Field(Unicode(256))

    recipes = OneToMany(
        'Recipe', inverse='author', order_by='-last_updated')
    user_settings = OneToMany(
        'UserSetting',
        cascade='all, delete-orphan',
        collection_class=attribute_mapped_collection('name')
    )
    settings = AssociationProxy(
        'user_settings',
        'value',
        creator=lambda name, value: UserSetting(name=name, value=value)
    )

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
    def printed_name(self):
        if self.full_name.strip():
            return self.full_name.strip()
        return self.username

    @property
    def printed_first_name(self):
        if self.first_name and self.first_name.strip():
            return self.first_name.strip()
        return self.username

    @property
    def abbreviated_name(self):
        if self.first_name and self.last_name:
            return "%s %s." % (self.first_name, self.last_name[0])
        return self.username

    @property
    def password(self):
        return self._password

    @password.setter  # noqa
    def password(self, v):
        self._password = self.__hash_password__(v)

    @property
    def published_recipes(self):
        return filter(lambda r: r.state == "PUBLISHED", self.recipes)

    @property
    def drafts(self):
        return filter(
            lambda r: r.state == "DRAFT" and r.published_version is None,
            self.recipes
        )

    @property
    def gravatar(self):
        return 'http://www.gravatar.com/avatar/%s?d=https://draughtcraft.com/images/glass-square.png' % (
            md5(self.email.strip().lower()).hexdigest()
        )

    @classmethod
    def __hash_password__(cls, plain, salt=None):
        if salt is None:
            salt = b64encode(urandom(6))
        if ':' not in salt:
            salt = '%s:' % salt
        salt = salt.split(':')[0]
        return '%s:%s' % (salt, b64encode(
            PBKDF2(plain, salt, iterations=16000).read(32)
        ))

    @classmethod
    def validate(cls, username, password):
        # Lookup the user
        user = cls.get_by(username=username)
        if user:
            salt = user.password.split(':')[0]
            pbk = cls.__hash_password__(password, salt)

            # If PBKDF2 matches...
            match = cls.query.filter(and_(
                cls.username == username,
                cls.password == pbk
            )).first()
            if match is not None:
                return match

            # Otherwise the user might have a sha256 password
            salt = getattr(
                getattr(conf, 'session', None),
                'password_salt',
                'example'
            )
            sha = sha256(password + salt).hexdigest()

            # If sha256 matches...
            match = cls.query.filter(and_(
                cls.username == username,
                cls.password == sha
            )).first()
            if match is not None:
                # Overwrite to use PBKDF2 in the future
                user.password = password
                return match


class UserSetting(Entity):
    user = ManyToOne('User')
    name = Field(Unicode(64), index=True)
    _value = Field(UnicodeText)

    __defaults__ = {
        'default_ibu_formula': 'tinseth',
        'default_recipe_volume': 5,
        'default_recipe_type': 'MASH',
        'unit_system': 'US',
        'brewhouse_efficiency': .75
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

    @value.setter  # noqa
    def value(self, v):
        self._value = dumps(v)


class PasswordResetRequest(Entity):
    code = Field(Unicode(64), primary_key=True)
    datetime = Field(DateTime)

    user = ManyToOne('User')
