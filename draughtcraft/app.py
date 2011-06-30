from pecan                  import make_app
from pecan.hooks            import TransactionHook
from draughtcraft           import model
from draughtcraft.templates import helpers
from beaker.middleware      import SessionMiddleware

def setup_app(config):

    def add_middleware(app):
        options = getattr(config, 'session', {})
        return SessionMiddleware(app, **options)
    
    model.init_model()
    
    return make_app(
        config.app.root,
        static_root     = config.app.static_root,
        debug           = config.app.debug,
        wrap_app        = add_middleware,
        logging         = config.app.logging,
        template_path   = config.app.template_path,
        force_canonical = config.app.force_canonical,
        hooks           = [
             TransactionHook(
                 model.start,
                 model.start,
                 model.commit,
                 model.rollback,
                 model.clear
             )
        ],   
        extra_template_vars = dict(
            h           = helpers
        )
    )
