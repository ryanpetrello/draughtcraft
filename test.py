from draughtcraft.controllers.root import RootController

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
    'reload'        : True,
    'debug'         : True,
    'logging'       : False,
    'errors'        : {
        '404'            : '/error/404',
        '__force_dict__' : True
    }
}

sqlalchemy = {
    'url'           : 'sqlite://',
    'echo'          : False,
    'echo_pool'     : False,
    'pool_recycle'  : 3600,
    'encoding'      : 'utf-8'
}

session = {
    'key'            : 'draughtcraft',
    'type'           : 'cookie',
    'validate_key'   : 'example',
    '__force_dict__' : True
}
