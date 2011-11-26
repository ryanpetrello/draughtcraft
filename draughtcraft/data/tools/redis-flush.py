from pecan.commands.base            import Command
import sys

def redis_connector():
    from pecan import conf
    from redis import Redis
    return Redis(**conf.redis)


class EnvCommand(Command):
    """
    Load a pecan environment (namely, database initialization and binding).
    """
    
    # command information
    usage = 'CONFIG_NAME'
    summary = __doc__.strip().splitlines()[0].rstrip('.')
    
    # command options/arguments
    min_args = 1
    max_args = 1
    
    def command(self):
        
        # load the config and the app
        config = self.load_configuration(self.args[0])
        setattr(config.app, 'reload', False)
        self.load_app(config)

        # establish the model for the app
        self.load_model(config)


BLUE = '\033[94m'
ENDS = '\033[0m'

def flush():
    """ Used to flush the redis resource cache """

    print "="*80
    print BLUE + "FLUSHING CACHE" + ENDS
    print "="*80
    EnvCommand('env').run([sys.argv[1]])

    redis = redis_connector()
    redis.flushdb()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        flush()
    else:
        print 'Usage: python redis-flush.py /path/to/config.py'
