from draughtcraft.controllers.root  import RootController

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
    'url'           : 'sqlite:///draughtcraft.db',
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

postmark = {
    'api_key'       : 'POSTMARK_API_TEST'
}
