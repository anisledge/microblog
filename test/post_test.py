#Avoid import errors: add google directories to the path
import sys
import os
sys.path.insert(1, "/Users/Ani/Downloads/google-cloud-sdk/lib/third_party")
sys.path.insert(1, "/Users/Ani/Downloads/google-cloud-sdk/platform/google_appengine")
sys.path.insert(1, "/Users/Ani/Downloads/google-cloud-sdk/platform/google_appengine")
sys.path.insert(0, os.path.join('..', os.path.dirname(__file__)))

#Import necessary files for testing
from google.appengine.ext import testbed
from google.appengine.api import datastore
import unittest
import webtest
import blog

#Setup jinja2 templates
import jinja2
template_dir = os.path.join('..', os.path.dirname(__file__), 'templates')
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

        self.post = blog.Post(subject="test", content="test", author=user, parent=blog.blog_key())
        self.post.put()
        self.post_id = str(self.post.key().id())
        
    def tearDown(self):
        self.testbed.deactivate()

    def login(self):
        response = self.testapp.get('/login')
        form = response.form
        form['username'] = self.user.username
        form['password'] = self.password
        valid_login = form.submit()
        valid_login.follow()

    def test_post_handler(self):
        response = self.testapp.get('/post/' + self.post_id)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('post/post.html', post=self.post))
    
    def test_create_post_handler_unauth(self):
        response = self.testapp.get('/post/new')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))

    def test_edit_post_handler_unauth(self):
        response = self.testapp.get('/post/' + self.post_id + '/edit')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))

    def test_delete_post_handler_unauth(self):
        response = self.testapp.get('/post/' + self.post_id + '/delete')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))
    
    def test_create_post_handler(self):
        self.login()

        response = self.testapp.get('/post/new')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('post/new.html'))

    def test_create_post_valid(self):
        self.login()

        response = self.testapp.get('/post/new')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['subject'] = 'testCreate'
        form['content'] = 'testCreate'

        valid_create = form.submit()
        self.assertEqual(valid_create.status_int, 302)

    def test_create_post_invalid(self):
        self.login()

        response = self.testapp.get('/post/new')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['subject'] = ''
        form['content'] = 'Nope'

        invalid_create = form.submit()
        self.assertEqual(invalid_create.status_int, 200)

        self.assertEqual(invalid_create.body, template('post/new.html', subject="", blog_content="Nope", error=True))
        self.assertEqual(form['subject'].value, "")
        self.assertEqual(form['content'].value, "Nope")

    def test_edit_post_handler(self):
        self.login()

        response = self.testapp.get('/post/' + self.post_id + '/edit')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('post/edit.html', post=self.post))

    def test_edit_post_valid(self):
        self.login()

        response = self.testapp.get('/post/' + self.post_id + '/edit')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['subject'] = 'NewSubject'
        form['content'] = 'NewContent'

        valid_edit = form.submit()
        self.assertEqual(valid_edit.status_int, 302)

    def test_edit_post_invalid(self):
        self.login()

        response = self.testapp.get('/post/' + self.post_id + '/edit')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['subject'] = ''
        form['content'] = ''

        invalid_edit = form.submit()
        self.assertEqual(invalid_edit.status_int, 200)
        
        form = invalid_edit.form
        self.assertEqual(invalid_edit.body, template('post/edit.html', post=self.post, error=True))
        self.assertEqual(form['subject'].value, self.post.subject)
        self.assertEqual(form['content'].value, self.post.content)

    def test_delete_post_handler(self):
        self.login()
        
        response = self.testapp.get('/post/' + self.post_id + '/delete')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('post/delete.html', post=self.post))

suite = unittest.TestLoader().loadTestsFromTestCase(AppTest)
unittest.TextTestRunner(verbosity=2).run(suite)