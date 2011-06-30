from elixir     import Entity, Field, Unicode, DateTime, OneToMany
from pecan      import conf
from datetime   import datetime
from hashlib    import sha256, md5


class User(Entity):

    first_name  = Field(Unicode(64))
    last_name   = Field(Unicode(64))

    username    = Field(Unicode(64), unique=True)
    _password   = Field(Unicode(64), colname='password', synonym='password')
    email       = Field(Unicode(64), index=True)
    signup_date = Field(DateTime, default=datetime.utcnow)

    recipes     = OneToMany('Recipe', inverse='author')

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, v):
        self._password = self.__hash_password__(v)

    @property
    def gravatar(self):
        return 'http://www.gravatar.com/avatar/%s' % (
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
