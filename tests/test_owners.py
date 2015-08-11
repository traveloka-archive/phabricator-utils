import os
import request_review
import unittest

class GetOwnersTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir('tests/fs')

    @classmethod
    def tearDownClass(cls):
        os.chdir('../..')

    def test_mod1_python(self):
        owners = request_review.get_owners("module1/foo.py")
        reviewers = owners['reviewers']
        self.assertTrue('#mod1' in reviewers)
        self.assertTrue('#python' in reviewers)

    def test_mod1_other(self):
        owners = request_review.get_owners("module1/bar.c")
        reviewers = owners['reviewers']
        self.assertTrue('#mod1' in reviewers)
        self.assertFalse('#python' in reviewers)
        

if __name__ == '__main__':
    unittest.main()        
