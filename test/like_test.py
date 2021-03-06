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
        self.user = blog.User(username='test1', password=pw_hash, email="", parent=blog.blog_key())
        self.user.put()
        self.user_id = str(self.user.key().id())
        self.password = 'password'

        pw_hash2 = 'ea1472a39162c51a2f53d73107f7b2ffffa94f901c99ed11f5fc28126b48bf39|vPnoC'
        self.user2 = blog.User(username='test2', password=pw_hash2, email="", parent=blog.blog_key())
        self.user2.put()

        self.post = blog.Post(subject="test", content="test", author=self.user2, parent=blog.blog_key())
        self.post.put()
        self.post_id = str(self.post.key().id())
        
    def tearDown(self):
        self.testbed.deactivate()

    def login1(self):
        response = self.testapp.get('/login')
        form = response.form
        form['username'] = self.user.username
        form['password'] = self.password
        valid_login = form.submit()
        valid_login.follow()

    def login2(self):
        response = self.testapp.get('/login')
        form = response.form
        form['username'] = self.user2.username
        form['password'] = self.password
        valid_login = form.submit()
        valid_login.follow()
    
    def test_like_handler(self):
        self.login1()
        self.assertEqual(len(self.post.likes.fetch(limit=20)), 0)
        
        response = self.testapp.post('/post/' + self.post_id + '/like')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('post/post.html', post=self.post))
        
        self.assertEqual(len(self.post.likes.fetch(limit=20)), 1)
        #users can only have one like at a time per post
        response = self.testapp.post('/post/' + self.post_id + '/like')
        response = response.follow()

        self.assertEqual(len(self.post.likes.fetch(limit=20)), 1)

    def test_like_handler_unauth(self):
        response = self.testapp.post('/post/' + self.post_id + '/like')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))

        #can't like own post
        self.login2()
        response = self.testapp.post('/post/' + self.post_id + '/like')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))

    def test_unlike_handler(self):
        like = blog.Like(post=self.post, author=self.user, parent=blog.blog_key())
        like.put()
        self.login1()
        self.assertEqual(len(self.post.likes.fetch(limit=20)), 1)
        
        response = self.testapp.post('/post/' + self.post_id + '/unlike')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('post/post.html', post=self.post))
        
        self.assertEqual(len(self.post.likes.fetch(limit=20)), 0)

    def test_unlike_handler_unauth(self):
        response = self.testapp.post('/post/' + self.post_id + '/like')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))

        #can't unlike own post
        self.login2()
        response = self.testapp.post('/post/' + self.post_id + '/unlike')
        self.assertEqual(response.status_int, 302)
        response = response.follow()
        self.assertEqual(response.body, template('user/signup.html'))

suite = unittest.TestLoader().loadTestsFromTestCase(AppTest)
unittest.TextTestRunner(verbosity=2).run(suite)