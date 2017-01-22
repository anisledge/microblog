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
    
    def test_like_handler(self):
        response = self.testapp.post('/post/' + self.post_id + '/like')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "Allows users to like post %s" % self.post_id)

    def test_unlike_handler(self):
        response = self.testapp.post('/post/' + self.post_id + '/unlike')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, "Allows users to unlike post %s" % self.post_id)

suite = unittest.TestLoader().loadTestsFromTestCase(AppTest)
unittest.TextTestRunner(verbosity=2).run(suite)