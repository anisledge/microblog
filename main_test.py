# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#TEST DATA
signup_valid = { 'username': 'test', 'password': 'test1234', 'verify': 'test1234', 'email': 'test@test.com'}
signup_invalid = { 'username': '">ha', 'password': '', 'verify': 'test123', 'email': 'test' }
signup_error = { 'username': True, 'password': True, 'verify': True, 'email': True}
login_valid = { 'username': 'test', 'password': 'test1234' }
login_invalid = { 'username': '', 'password': '' }

import webtest
import blog
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
    autoescape = True)

def template(template, **params):
    return jinja_env.get_template(template).render(params)

def test_get():
    app = webtest.TestApp(blog.app)

    #USER ROUTING
    signup = app.get('/signup')
    assert signup.status_int == 200
    assert signup.body == template('signup.html')

    login = app.get('/login')
    assert login.status_int == 200
    assert login.body == template('login.html')

    logout = app.get('/logout')
    assert logout.status_int == 302
    logout = logout.follow()
    assert logout.body == template('signup.html')
    
    user = app.get('/user?username=test')
    assert user.status_int == 200
    assert user.body == template('user.html', username='test')
	
    #SIGNUP FORM
    signup_form = signup.form
    assert signup_form.method == 'POST'
    
    assert signup_error, False == blog.detect_errors(signup_invalid['username'], signup_invalid['password'], 
        signup_invalid['verify'], signup_invalid['email'])

    #INVALID
    signup_form['username'] = signup_invalid['username']
    signup_form['password'] = signup_invalid['password']
    signup_form['verify'] = signup_invalid['verify']
    signup_form['email'] = signup_invalid['email']
    invalid_signup = signup_form.submit()

    error_form = template("signup.html", error=signup_error, username=signup_invalid['username'], email=signup_invalid['email'])
    assert invalid_signup.body == error_form
    
    signup_form = invalid_signup.form
    assert signup_form['username'].value == signup_invalid['username']
    assert signup_form['password'].value == ""
    assert signup_form['verify'].value == ""
    assert signup_form['email'].value == signup_invalid['email']

    #VALID
    signup_form['username'] = signup_valid['username']
    signup_form['password'] = signup_valid['password']
    signup_form['verify'] = signup_valid['verify']
    signup_form['email'] = signup_valid['email']
    valid_signup = signup_form.submit()
    
    assert valid_signup.status_int == 302
    valid_signup = valid_signup.follow()
    assert valid_signup.body == template('user.html', username=signup_valid['username'])

    #LOGIN FORM
    login_form = login.form
    assert login_form.method == 'POST'

    #INVALID
    login_form['username'] = login_invalid['username']
    login_form['password'] = login_invalid['password']
    invalid_login = login_form.submit()

    error_form = template('login.html', error=True, username=login_invalid['username'])
    assert invalid_login.body == error_form

    login_form = invalid_login.form
    assert login_form['username'].value == login_invalid['username']
    assert login_form['password'].value == ""
    
    #VALID
    login_form['username'] = login_valid['username']
    login_form['password'] = login_valid['password']
    valid_login = login_form.submit()
    
    assert valid_login.status_int == 302
    valid_login = valid_login.follow()
    assert valid_login.body == template('user.html', username=login_valid['username'])


test_get()
	
