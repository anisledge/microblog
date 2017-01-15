import hashlib
import hmac
import string
import random
import secrets

SECRET = secrets.get()

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return str("%s|%s" % (s, hash_str(s)))

def check_secure_val(h):
    s = h.split('|')[0]
    if make_secure_val(s) == h:
        return s

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(name + pw + salt).hexdigest()
  return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
  salt = h.split('|')[1]
  return h == make_pw_hash(name, pw, salt)