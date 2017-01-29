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

        self.comment = blog.Comment(text="test", author=self.user, post=self.post, parent=blog.blog_key())
        self.comment.put()
        self.comment_id = str(self.comment.key().id())
        
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
    
    def test_create_comment_handler(self):
        response = self.testapp.get('/post/' + self.post_id + '/comment/new')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('comment/new.html', post=self.post))

    def test_create_comment_valid(self):
        self.login1()
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)

        response = self.testapp.get('/post/' + self.post_id + '/comment/new')
        form = response.form
        self.assertEqual(form.method, 'POST')

        form['text'] = "test-create"
        valid_create = form.submit()
        self.assertEqual(valid_create.status_int, 302)
        
        response = valid_create.follow()
        self.assertEqual(response.body, template('post/post.html', post=self.post))
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 2)

    def test_create_comment_invalid(self):
        self.login1()
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)

        response = self.testapp.get('/post/' + self.post_id + '/comment/new')
        form = response.form
        self.assertEqual(form.method, 'POST')
        
        form['text'] = ''
        invalid_create = form.submit()
        self.assertNotEqual(invalid_create.status_int, 302)
        self.assertEqual(invalid_create.body, template('comment/new.html', post=self.post, error=True))
        self.assertEqual(invalid_create.form['text'].value, '')
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)

    def test_edit_comment_handler(self):
        response = self.testapp.get('/post/' + self.post_id + '/comment/' + self.comment_id + '/edit')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('comment/edit.html', comment=self.comment, post=self.post))
        

        self.assertEqual(response.form['text'].value, self.comment.text)

    def test_edit_comment_valid(self):
        self.login1()
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)
        comment = blog.Comment.get_by_id(int(self.comment_id), parent=blog.blog_key())
        self.assertEqual(str(comment.text), 'test')

        response = self.testapp.get('/post/' + self.post_id + '/comment/' + self.comment_id + '/edit')
        form = response.form
        self.assertEqual(form.method, 'POST')
        
        form['text'] = 'test-edit'
        valid_edit = form.submit()
        self.assertEqual(valid_edit.status_int, 302)

        response = valid_edit.follow()
        self.assertEqual(response.body, template('post/post.html', post=self.post))
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)

        comment = blog.Comment.get_by_id(int(self.comment_id), parent=blog.blog_key())
        self.assertEqual(str(comment.text), 'test-edit')

    def test_edit_comment_invalid(self):
        self.login1()
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)
        comment = blog.Comment.get_by_id(int(self.comment_id), parent=blog.blog_key())
        self.assertEqual(str(comment.text), 'test')

        response = self.testapp.get('/post/' + self.post_id + '/comment/' + self.comment_id + '/edit')
        form = response.form
        self.assertEqual(form.method, 'POST')
        
        form['text'] = ''
        invalid_edit = form.submit()
        self.assertNotEqual(invalid_edit.status_int, 302)
        
        self.assertEqual(invalid_edit.body, template('comment/edit.html', comment=self.comment, post=self.post, error=True))
        self.assertEqual(invalid_edit.form['text'].value, comment.text)

        comment = blog.Comment.get_by_id(int(self.comment_id), parent=blog.blog_key())
        self.assertEqual(str(comment.text), 'test')

    def test_delete_comment_handler(self):
        response = self.testapp.get('/post/' + self.post_id + '/comment/' + self.comment_id + '/delete')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, template('comment/delete.html', comment=self.comment, post=self.post))

    def test_delete_comment_valid(self):
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 1)

        response = self.testapp.get('/post/' + self.post_id + '/comment/' + self.comment_id + '/delete')
        form = response.form
        self.assertEqual(form.method, 'POST')
        valid_delete = form.submit()
        self.assertEqual(valid_delete.status_int, 302)

        response = valid_delete.follow()
        self.assertEqual(response.body, template('post/post.html', post=self.post))
        
        self.assertEqual(len(self.post.comments.fetch(limit=20)), 0)

suite = unittest.TestLoader().loadTestsFromTestCase(AppTest)
unittest.TextTestRunner(verbosity=2).run(suite)