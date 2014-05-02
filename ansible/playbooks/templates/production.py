import time

from draughtcraft.lib.minify import FileSystemResourceCache

# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}


# Pecan Application Configurations
app = {
    'root': 'draughtcraft.controllers.root.RootController',
    'modules': ['draughtcraft'],
    'static_root': '%(confdir)s/public',
    'template_path': '%(confdir)s/draughtcraft/templates',
    'stamp': time.time(),
    'logging': False,
    'errors': {
        404: '/error/404/',
        500: '/error/500/',
        '__force_dict__': True
    }
}

sqlalchemy = {
    'url': 'postgresql+psycopg2://localhost/draughtcraftdev',
    'echo': False,
    'echo_pool': False,
    'pool_recycle': 3600,
    'encoding': 'utf-8'
}

signups = {
    'bcc': '{{ bcc_address }}'
}

session = {
    'key': 'draughtcraft',
    'type': 'cookie',
    'validate_key': '{{ session_key }}',
    '__force_dict__': True
}

cache = {
    'key': 'resources_to_compile',
    'data_backend': FileSystemResourceCache,
    '__force_dict__': True
}

postmark = {
    'api_key': '{{ postmark_api_key }}'
}
