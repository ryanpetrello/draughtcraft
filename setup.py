from setuptools import setup, find_packages

from draughtcraft import __version__

setup(
    name='draughtcraft',
    version=__version__,
    description='Recipe builder and community app for homebrewing enthusiasts',
    author='Ryan Petrello',
    author_email='ryan (at) draughtcraft.com',
    install_requires=[
        "pecan >= 0.4",
        "pecan_wtforms",
        "sqlalchemy == 0.7.8",
        "elixir",
        "beaker",
        "genshi",
        "webhelpers",
        "python-postmark",
        "BeautifulSoup",
        "pbkdf2",
        "lesscpy==0.9j",
        "jsmin == 2.0.2",
        "psycopg2",
        "fudge",
        "boto"
    ],
    zip_safe=False,
    include_package_data=True,
    test_suite='draughtcraft.tests',
    tests_require=['selenium'],
    package_data={
        'draughtcraft': ['*.db'],
    },
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [pecan.command]
    populate=draughtcraft.data.tools.populate:PopulateCommand
    flush=draughtcraft.data.tools.cacheflush:RedisFlushCommand
    cdn-upload=draughtcraft.data.tools.cdn:CDNUpload
    """
)
