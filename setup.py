# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from draughtcraft import __version__

setup(
    name = 'draughtcraft',
    version = __version__,
    description = 'Recipe builder and community app for homebrewing enthusiasts.',
    author = 'Ryan Petrello',
    author_email = 'ryan (at) draughtcraft.com',
    install_requires = [
        "pecan",
        "elixir",
        "beaker",
        "formencode",
        "genshi",
        "webhelpers",
        "webflash",
        "simplejson",
        "python-postmark",
        "BeautifulSoup",
        "pytest-xdist",
        "pytest-cov",
        "redis",
        "hiredis",
        "lesspy",
        "jsmin",
        "psycopg2",
        "fudge"
    ],
    zip_safe = False,
    paster_plugins = ['Pecan'],
    include_package_data = True,
    package_data = {
        'draughtcraft': ['*.db'],
    },
    packages = find_packages(exclude=['ez_setup'])
)
