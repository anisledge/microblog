#Avoid import errors: add google directories to the path
import sys
sys.path.insert(1, "/Users/Ani/Downloads/google-cloud-sdk/lib/third_party")
sys.path.insert(1, "/Users/Ani/Downloads/google-cloud-sdk/platform/google_appengine")

#Import necessary files for testing
from google.appengine.ext import testbed
from google.appengine.api import datastore
import unittest
import webtest
import blog

#Setup jinja2 templates
import os
import jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
   autoescape = True)

def template(template, **params):
    return jinja_env.get_template(template).render(params)

#Test class
class AppTest(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(blog.app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

        #Test User
        pw_hash = '472f43f061676da04375012af4b9ae48d87b2f6fbedb4f9f64e8923d24b6e391|gLGkF'
        user = blog.User(username='test1', password=pw_hash, email="", parent=blog.blog_key())
        user.put()
        self.user = user
        self.user_id = str(self.user.key().id())
        self.password = 'password'
        
    def tearDown(self):
        self.testbed.deactivate()

    def test_signup_handler(self):
        response = self.testapp.get('/signup')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('signup.html'))

    def test_signup_valid(self):
        response = self.testapp.get('/signup')
        form = response.form
        self.assertEqual(form.method, 'POST')

        valid_input = { 'username': 'test', 
                        'password': 'test1234', 
                        'verify': 'test1234', 
                        'email': 'test@test.com'}

        form['username'] = valid_input['username']
        form['password'] = valid_input['password']
        form['verify'] = valid_input['verify']
        form['email'] = valid_input['email']
        
        valid_signup = form.submit()
        self.assertEqual(valid_signup.status_int, 302)
        valid_signup = valid_signup.follow()
        self.assertEqual(valid_signup.body, template('user.html', username=valid_input['username']))

    def test_signup_invalid(self):
        response = self.testapp.get('/signup')
        form = response.form
        self.assertEqual(form.method, 'POST')

        invalid_input = { 'username': '">ha', 
                          'password': '',
                          'verify': 'test123', 
                          'email': 'test' }
        
        form['username'] = invalid_input['username']
        form['password'] = invalid_input['password']
        form['verify'] = invalid_input['verify']
        form['email'] = invalid_input['email']
        
        invalid_signup = form.submit()

        error = { 'username': True, 'password': True, 'verify': True, 'email': True}

        error_form = template("signup.html", error=error, username=invalid_input['username'], email=invalid_input['email'])
        self.assertEqual(invalid_signup.body, error_form)
        
        form = invalid_signup.form
        self.assertEqual(form['username'].value, invalid_input['username'])
        self.assertEqual(form['password'].value, "")
        self.assertEqual(form['verify'].value, "")
        self.assertEqual(form['email'].value, invalid_input['email'])

    def test_login_handler(self):
        response = self.testapp.get('/login')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('login.html'))

    def test_login_valid(self):
        response = self.testapp.get('/login')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['username'] = self.user.username
        form['password'] = self.password
        
        valid_login = form.submit()
        self.assertEqual(valid_login.status_int, 302)
        valid_login = valid_login.follow()
        self.assertEqual(valid_login.body, template('user.html', username=self.user.username))

    def test_login_invalid(self):
        response = self.testapp.get('/login')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['username'] = "nope"
        form['password'] = ""
        
        invalid_login = form.submit()

        error_form = template('login.html', error=True, username="nope")
        self.assertEqual(invalid_login.body, error_form)

        form = invalid_login.form
        self.assertEqual(form['username'].value, "nope")
        self.assertEqual(form['password'].value, "")

    def test_logout_handler(self):
        response = self.testapp.get('/logout')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('signup.html'))

    def test_user_handler(self):
        response = self.testapp.get('/user/' + self.user_id)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('user.html', username='test1'))

suite = unittest.TestLoader().loadTestsFromTestCase(AppTest)
unittest.TextTestRunner(verbosity=2).run(suite)