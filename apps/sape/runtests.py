import sys
import os.path
import unittest
sys.path.append(os.path.realpath(os.path.dirname(__file__) + '/..'))

from sape import tests
suite = unittest.makeSuite(tests.SapeTestCase)
unittest.TextTestRunner().run(suite)
