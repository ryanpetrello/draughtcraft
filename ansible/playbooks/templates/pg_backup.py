from datetime import datetime
from cStringIO import StringIO
import gzip
import subprocess

import boto
from boto.s3.connection import OrdinaryCallingFormat

conn = boto.connect_s3(
    aws_access_key_id = '{{ dho_key }}',
    aws_secret_access_key = '{{ dho_secret }}',
    host = 'objects-us-west-1.dream.io',
    calling_format = OrdinaryCallingFormat()
)

gzio = StringIO()
gzfile = gzip.GzipFile(fileobj=gzio, mode='w')
gzfile.write(subprocess.Popen(
    ['pg_dump', '{{ dbname }}'],
    stdout=subprocess.PIPE
).communicate()[0])
gzfile.close()

bucket = conn.get_bucket('{{ backup_bucket }}')
key = bucket.new_key(datetime.utcnow().isoformat())
key.set_contents_from_string(gzio.getvalue())
key.set_canned_acl('private')
