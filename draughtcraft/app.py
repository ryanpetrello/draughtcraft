from collections import namedtuple
import os

from beaker.middleware import SessionMiddleware, CacheMiddleware
from lesscpy.scripts.compiler import ldirectory
from pecan import make_app
from pecan.hooks import TransactionHook

from draughtcraft import model
from draughtcraft.lib.auth import AuthenticationHook
from draughtcraft.lib.minify import ResourceLookupMiddleware
from draughtcraft.templates import helpers

def setup_app(config):

    def add_middleware(app):
        app = ResourceLookupMiddleware(app)
        options = getattr(config, 'cache', {})
        app = CacheMiddleware(app, **options)
        options = getattr(config, 'session', {})
        return SessionMiddleware(app, **options)

    model.init_model()

    # Compile .less resources
    LessConfig = namedtuple(
        'LessConfig',
        ['min_ending', 'minify', 'xminify', 'debug', 'force', 'verbose',
         'recurse', 'dry_run']
    )

    ldirectory(
        os.path.join(config.app.static_root, '_precompile'),
        os.path.join(config.app.static_root, 'css'),
        LessConfig(
            min_ending=False,
            minify=True,
            xminify=False,
            debug=config.app.debug,
            force=False,
            verbose=False,
            recurse=True,
            dry_run=False
        ),
        None
    )

    return make_app(
        config.app.root,
        static_root=config.app.static_root,
        template_path=config.app.template_path,
        wrap_app=add_middleware,
        logging=config.app.logging,
        debug=getattr(config.app, 'debug', False),
        force_canonical=getattr(config.app, 'force_canonical', True),
        errors={
            404: '/error/404',
            401: '/error/401',
            403: '/error/403',
            500: '/error/500'
        },
        hooks=[
            TransactionHook(
                model.start,
                model.start,
                model.commit,
                model.rollback,
                model.clear
            ),
            AuthenticationHook()
        ],
        extra_template_vars=dict(
            h=helpers
        )
    )
