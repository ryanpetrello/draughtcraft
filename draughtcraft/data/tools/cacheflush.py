from pecan.commands.base import BaseCommand

BLUE = '\033[94m'
ENDS = '\033[0m'


def redis_connector():
    from pecan import conf
    from redis import Redis
    return Redis(**conf.redis)


class RedisFlushCommand(BaseCommand):
    """
    Flush the Redis resource cache.
    """

    def run(self, args):
        super(RedisFlushCommand, self).run(args)
        self.load_app()

        print "=" * 80
        print BLUE + "FLUSHING CACHE" + ENDS
        print "=" * 80

        redis = redis_connector()
        redis.flushdb()
