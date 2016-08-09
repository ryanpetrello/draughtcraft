import os.path
from datetime import datetime, timedelta

import boto
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat
from pecan.commands.base import BaseCommand

import draughtcraft

ALLOWED_TYPES = ('gif', 'png', 'jpg', 'css', 'js', 'ico')

BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
ENDS = '\033[0m'


class CDNUpload(BaseCommand):
    """
    Upload static files to the CDN
    """

    arguments = ({
        'name': 'access_key',
        'help': 'DHO Access Key'
    }, {
        'name': 'secret_key',
        'help': 'DHO Secret Key'
    }, {
        'name': 'bucket_name',
        'help': 'DHO Bucket Name'
    },)

    def run(self, args):
        super(CDNUpload, self).run(args)

        print "=" * 80
        print BLUE + "UPLOADING STATIC RESOURCES" + ENDS
        print "=" * 80

        conn = boto.connect_s3(
            aws_access_key_id=args.access_key,
            aws_secret_access_key=args.secret_key,
            host='objects-us-west-1.dream.io',
            calling_format=OrdinaryCallingFormat()
        )
        bucket = conn.get_bucket(args.bucket_name)
        path = os.path.join(
            os.path.dirname(draughtcraft.__file__),
            '..',
            'public'
        )
        expires = datetime.utcnow() + timedelta(days=(25 * 365))
        expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        metadata = {'Expires': expires}
        for dirpath, dirnames, files in os.walk(path):
            for f in files:
                filename = os.path.relpath(os.path.join(dirpath, f), path)
                if filename.endswith(ALLOWED_TYPES):
                    print GREEN + filename + ENDS
                    key = bucket.get_key(filename)
                    if key is None:
                        key = Key(bucket)
                        key.key = filename
                    key.set_contents_from_filename(
                        os.path.join(dirpath, f),
                        headers=metadata
                    )
                    bucket.set_acl('public-read', key)
                else:
                    print RED + filename + ENDS
