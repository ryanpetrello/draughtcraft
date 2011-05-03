from pecan                  import make_app
from pecan.hooks            import TransactionHook
from beerparts              import model
from beerparts.templates    import helpers

def setup_app(config):
    
    model.init_model()
    
    return make_app(
        config.app.root,
        static_root     = config.app.static_root,
        debug           = config.app.debug,
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
