import webapp2
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

class Handler(webapp2.RequestHandler):
	def render(self, template, **params):
		t = jinja_env.get_template(template)
		self.response.out.write(t.render(params))

class Signup(Handler):
	def get(self):
		self.render('signup.html')

	def post(self):
		pass

class Login(Handler):
	def get(self):
		self.render('login.html')

	def post(self):
		pass

class Logout(Handler):
	def get(self):
		self.redirect('/signup')

class UserHandler(Handler):
	def get(self):
		self.render('user.html')

app = webapp2.WSGIApplication([('/signup', Signup),
							('/login', Login),
							('/logout', Logout),
							('/user', UserHandler),
							],
							debug=True)