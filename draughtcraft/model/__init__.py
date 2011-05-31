from pecan              import conf
from sqlalchemy         import create_engine
from sqlalchemy.orm     import scoped_session, sessionmaker

import elixir

elixir.options_defaults.update({
    'shortnames': True
})

Session = scoped_session(sessionmaker())
elixir.session = Session
metadata = elixir.metadata

def _engine_from_config(configuration):
    configuration = dict(configuration)
    url = configuration.pop('url')
    return create_engine(url, **configuration)

def init_model():
    conf.sqlalchemy.sa_engine = _engine_from_config(conf.sqlalchemy)

def bind(target):
    Session.bind = target
    metadata.bind = Session.bind

def start():
    bind(conf.sqlalchemy.sa_engine)

def commit():
    Session.commit()

def rollback():
    Session.rollback()

def clear():
    Session.remove()

from ingredients    import *
from recipes        import *
from styles         import *

elixir.setup_all()
