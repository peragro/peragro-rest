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
    'install_requires': ['damn_index', 'django_project', 'django-mptt'],
    'test_requires': [],
    'packages': ['damn_rest'],
    'scripts': [],
    'name': 'damn_rest',
}

setup(**config)
