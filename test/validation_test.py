import sys
import os
sys.path.insert(0, os.path.join('..', os.path.dirname(__file__)))

import unittest
import re
import validation

#Test class
class ValidationTest(unittest.TestCase):
    def setUp(self):
    	pass

    def test_valid_username(self):
    	#rejects a blank username
    	self.assertFalse(validation.valid_username(""))

    	#rejects a username with special characters
    	self.assertFalse(validation.valid_username("%%/@#sdfjs"))

    	#accepts a username with alphanumerics, _ , or - 
    	self.assertTrue(validation.valid_username("test_test-123"))

    def test_valid_password(self):
    	#rejects a blank password
    	self.assertFalse(validation.valid_password(""))

    	#accepts a password with special characters
    	self.assertTrue(validation.valid_password("test123#@!%^"))

    def test_valid_email(self):
    	#rejects an incomplete email
    	self.assertFalse(validation.valid_email("test@"))
    	self.assertFalse(validation.valid_email("@test.com"))
    	self.assertFalse(validation.valid_email("test.com"))
    	
    	#accepts a blank email
    	self.assertTrue(validation.valid_email(""))

    	#accepts a valid email
    	self.assertTrue(validation.valid_email("test@test.com"))

    def test_detect_errors(self):
    	#invalid input returns false for error and valid
    	invalid = validation.detect_errors("$", "", "test", "123")
    	invalid_answer = ({ 'username': True, 'password': True, 'verify': True, 'email': True }, False)
    	self.assertTupleEqual(invalid, invalid_answer)

    	#valid input returns true for error and valid
    	valid = validation.detect_errors("test_test-123", "test123#^&/", "test123#^&/", "test@test.com")
    	valid_answer = ({ }, True)
    	self.assertTupleEqual(valid, valid_answer)

suite = unittest.TestLoader().loadTestsFromTestCase(ValidationTest)
unittest.TextTestRunner(verbosity=2).run(suite)