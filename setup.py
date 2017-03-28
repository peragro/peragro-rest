from __future__ import absolute_import
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Digital Assets Managed Neatly: REST-api',
    'author': 'sueastside',
    'url': 'https://github.com/sueastside/damn-rest',
    'download_url': 'https://github.com/sueastside/damn-rest',
    'author_email': 'No, thanks',
    'version': '0.1',
    'test_suite': 'tests.suite',
    'install_requires': ['django_project', 'django-mptt==0.7.4'],
    'test_requires': [],
    'packages': ['damn_rest'],
    'scripts': [],
    'name': 'damn_rest',
}

setup(**config)
