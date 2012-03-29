from sqlalchemy.pool import NullPool

# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'draughtcraft.controllers.root.RootController',
    'modules': ['draughtcraft'],
    'static_root': '%(confdir)s/../../public',
    'template_path': '%(confdir)s/../templates',
    'stamp': 'dev',
    'reload': True,
    'debug': True,
    'logging': False
}

sqlalchemy = {
    'url': 'postgresql+psycopg2://localhost/draughtcrafttest',
    'echo': False,
    'echo_pool': False,
    'pool_recycle': 3600,
    'encoding': 'utf-8',
    'poolclass': NullPool
}

signups = {
    'bcc': 'ryan@example.com'
}

session = {
    'key': 'draughtcraft',
    'type': 'cookie',
    'validate_key': 'example',
    '__force_dict__': True
}

cache = {
    'key': 'resources_to_compile',
    '__force_dict__': True
}

redis = {'__force_dict__': True}

postmark = {
    'api_key': 'POSTMARK_API_TEST'
}
