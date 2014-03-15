from pecan import make_app
from pecan.hooks import TransactionHook
from draughtcraft import model
from draughtcraft.lib.auth import AuthenticationHook
from draughtcraft.lib.minify import ResourceLookupMiddleware
from draughtcraft.templates import helpers
from lesspy import Less
from beaker.middleware import SessionMiddleware, CacheMiddleware

import os


def setup_app(config):

    def add_middleware(app):
        app = ResourceLookupMiddleware(app)
        options = getattr(config, 'cache', {})
        app = CacheMiddleware(app, **options)
        options = getattr(config, 'session', {})
        return SessionMiddleware(app, **options)

    model.init_model()

    # Compile .less resources
    Less(
        os.path.join(config.app.static_root, '_precompile'),
        os.path.join(config.app.static_root, 'css')
    ).compile()

    return make_app(
        config.app.root,
        static_root=config.app.static_root,
        template_path=config.app.template_path,
        wrap_app=add_middleware,
        logging=config.app.logging,
        debug=getattr(config.app, 'debug', False),
        force_canonical=getattr(config.app, 'force_canonical', True),
        errors = {
            '404': '/error/404',
            '401': '/error/401',
            '403': '/error/403',
            '500': '/error/500'
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
