from draughtcraft.controllers.root  import RootController
from draughtcraft.lib.minify        import RedisResourceCache

import draughtcraft

# Server Specific Configurations
server = {
    'port' : '8080',
    'host' : '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root'          : RootController(),
    'modules'       : [draughtcraft],
    'static_root'   : '%(confdir)s/public', 
    'template_path' : '%(confdir)s/draughtcraft/templates',
    'stamp'         : 'dev',
    'reload'        : True,
    'debug'         : True,
    'logging'       : False
}

sqlalchemy = {
    'url'           : 'postgresql+psycopg2://localhost/draughtcraftdev',
    'echo'          : False,
    'echo_pool'     : False,
    'pool_recycle'  : 3600,
    'encoding'      : 'utf-8'
}

signups = {
    'bcc'           : 'ryan@example.com'
}

session = {
    'key'               : 'draughtcraft',
    'type'              : 'cookie',
    'validate_key'      : 'example',
    '__force_dict__'    : True
}

cache = {
    'key'               : 'resources_to_compile',
    'data_backend'      : RedisResourceCache,
    '__force_dict__'    : True
}

redis = {
    'host'              : 'localhost',
    'port'              : 6379,
    'db'                : 0,
    '__force_dict__'    : True
}

postmark = {
    'api_key'       : 'POSTMARK_API_TEST'
}
