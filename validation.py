import re

USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+.[\S]+$")

def valid_username(username):
    return USER_RE.match(username)

def valid_password(password):
  return PASSWORD_RE.match(password)

def valid_email(email):
  if email:
    return EMAIL_RE.match(email)
  return True

def detect_errors(username, password, verify, email):
  error = {}
  valid = True
  if not (valid_username(username)):
    error["username"], valid = True, False
  if not (valid_password(password)):
    error["password"], valid = True, False
  if not (password == verify):
    error["verify"], valid = True, False
  if not (valid_email(email)):
    error["email"], valid = True, False 
  return error, valid