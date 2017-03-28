"""The tests collector used in setup.py"""
from __future__ import absolute_import
import os
import unittest


def suite():
    """Return a list of tests"""
    loader = unittest.TestLoader()
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    return loader.discover(directory, 'test_*.py')

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
