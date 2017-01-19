import webapp2 
import os 
import jinja2

from validation import detect_errors
from security import make_secure_val, check_secure_val, make_pw_hash, valid_pw
from google.appengine.ext import db
from model import User, Post

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
	def render(self, template, **params):
		t = jinja_env.get_template(template)
		self.response.out.write(t.render(params))

	def session_cookie(self, user_id):
		user_hash = make_secure_val(user_id)
		self.response.headers.add_header('Set-Cookie', 'user_id=' + user_hash)

	def valid_user_cookie(self):
		user_id_str = self.request.cookies.get('user_id')
		
		if user_id_str: 
			valid_id = check_secure_val(user_id_str)
			
			if valid_id:
				return User.get_by_id(int(valid_id), parent=blog_key())

class IndexHandler(Handler):
	def get(self):
		posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
		self.render("index.html", posts=posts)

class Signup(Handler):
	def get(self):
		self.render('user/signup.html')

	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email') 
 
		error, valid = detect_errors(user_username, user_password, user_verify, user_email)
		
		user = User.gql("WHERE username = '" + user_username + "'").get()
		
		if (user):
			error["username_exists"], valid = True, False

		if (valid): 
			pw_hash = make_pw_hash(user_username, user_password, salt=None)
			user = User(username=user_username, password=pw_hash, email=user_email, parent=blog_key())
			user.put()

			user_id = str(user.key().id())
			self.session_cookie(user_id)

			self.redirect("/user/%s" % str(user.key().id()))
		else:
			self.render("user/signup.html", error=error, username=user_username, email=user_email)

class Login(Handler):
	def get(self):
		self.render('user/login.html')

	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')

		user = User.gql("WHERE username = '" + user_username + "'").get()
		
		if user: 
			if valid_pw(user_username, user_password, user.password):
				user_id = str(user.key().id())
				self.session_cookie(user_id)
				self.redirect("/user/%s" % str(user.key().id()))	
				return
		
		self.render("user/login.html", error=True, username=user_username)

class Logout(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=')
		self.redirect('/signup')

class UserHandler(Handler):
	def get(self, user_id):		
		user = User.get_by_id(int(user_id), parent=blog_key())
		self.render("user/user.html", user=user)

class PostHandler(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		self.render("post/post.html", post=post)

class CreatePostHandler(Handler):
	def get(self):
		self.render('post/new.html')

	def post(self):
		user = self.valid_user_cookie()

		subject = self.request.get("subject")
		content = self.request.get("content")
		if subject and content:
			b = Post(subject=subject, content=content, author=user, parent=blog_key())
			b.put()
			self.redirect("/post/%s" % str(b.key().id()))
		else:
			self.render("post/new.html", subject=subject, blog_content=content, error=True)

class EditPostHandler(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		self.render('post/edit.html', post=post)

	def post(self, post_id):
		user = self.valid_user_cookie()
		post = Post.get_by_id(int(post_id), parent=blog_key())
		
		subject = self.request.get("subject")
		content = self.request.get("content")
		if subject and content:
			post.subject = subject
			post.content = content
			post.put()
			self.redirect('/post/%s' % post_id)
		else: 
			self.render("post/edit.html", post=post, error=True)
	
class DeletePostHandler(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		self.render("post/delete.html", post=post)

	def post(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		post.delete()
		self.redirect('/')

app = webapp2.WSGIApplication([('/', IndexHandler),
							('/signup', Signup),
							('/login', Login),
							('/logout', Logout),
							('/user/([0-9]+)', UserHandler),
							('/post/([0-9]+)', PostHandler),
							('/post/new', CreatePostHandler),
							('/post/([0-9]+)/edit', EditPostHandler),
							('/post/([0-9]+)/delete', DeletePostHandler),
							],
							debug=True)