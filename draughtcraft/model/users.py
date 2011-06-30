from elixir     import Entity, Field, Unicode, OneToMany
from pecan      import conf
from hashlib    import sha256


class User(Entity):

    first_name  = Field(Unicode(64))
    last_name   = Field(Unicode(64))

    username    = Field(Unicode(64), unique=True)
    _password   = Field(Unicode(64), colname='password', synonym='password')
    email       = Field(Unicode(64), index=True)

    recipes     = OneToMany('Recipe', inverse='author')

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, v):
        salt = getattr(
            getattr(conf, 'session', None), 
            'password_salt', 
            'example'
        )
        self._password = sha256(v + salt).hexdigest()
