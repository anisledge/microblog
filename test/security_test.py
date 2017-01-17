import sys
import os
sys.path.insert(0, os.path.join('..', os.path.dirname(__file__)))

import unittest
import re
import hashlib
import security

#Test class
class SecurityTest(unittest.TestCase):
    def setUp(self):
        self.contains_line = re.compile("\S+\|\S+")
        self.contains_test = re.compile("\S+\|test")
        self.a = "stringOne"
        self.b = "stringTwo"
    
    def test_make_secure_val(self):
        hash_a = security.make_secure_val(self.a)
        test_regex = self.contains_line.match(hash_a)
        self.assertTrue(bool(test_regex))
        
        hash_b = security.make_secure_val(self.b)
        self.assertNotEqual(hash_a, hash_b)

        md5 = hashlib.md5(self.a).hexdigest()
        self.assertNotEqual(hash_a, md5)

    def test_check_secure_val(self):
        hash_a = security.make_secure_val(self.a)
        hash_b = security.make_secure_val(self.b)
        false_a = "%s|%s" % (hash_a, "hgfuejidkskjhgyf")
        false_b = "%s|%s" % (hash_b, "reuidoskjnbhgvfg")

        self.assertEqual(security.check_secure_val(hash_a), self.a)
        self.assertEqual(security.check_secure_val(hash_b), self.b)
        self.assertIsNone(security.check_secure_val(false_a))
        self.assertIsNone(security.check_secure_val(false_b))

    def test_make_pw_hash(self):
        salt_a = security.make_pw_hash(self.a, "password")
        test_regex = self.contains_line.match(salt_a)
        self.assertTrue(bool(test_regex))

        salt_a_2 = security.make_pw_hash(self.a, "password")
        self.assertNotEqual(salt_a, salt_a_2)

        salt_a = security.make_pw_hash(self.a, "password", "test")
        salt_b = security.make_pw_hash(self.b, "password", "test")
        self.assertNotEqual(salt_a, salt_b)

        test_regex = self.contains_test.match(salt_a)
        self.assertTrue(bool(test_regex))

    def test_valid_pw(self):
        password_hash = security.make_pw_hash(self.a, "password")
        self.assertTrue(security.valid_pw(self.a, "password", password_hash))
        self.assertFalse(security.valid_pw(self.a, "wrong", password_hash))

suite = unittest.TestLoader().loadTestsFromTestCase(SecurityTest)
unittest.TextTestRunner(verbosity=2).run(suite)