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
    
    user = app.get('/user')
    assert user.status_int == 200
    assert user.body == template('user.html')
	
test_get()
	
