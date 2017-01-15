import webapp2
import os
import jinja2
from validation import detect_errors

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
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email') 
 
		error, valid = detect_errors(user_username, user_password, user_verify, user_email)
		
		if (valid): 
			self.redirect("/user?username=%s" % user_username)
		else:
			self.render("signup.html", error=error, username=user_username, email=user_email)

class Login(Handler):
	def get(self):
		self.render('login.html')

	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		
		if (user_username and user_password):
			self.redirect("/user?username=%s" % user_username)
		else:
			self.render("login.html", error=True, username=user_username)

class Logout(Handler):
	def get(self):
		self.redirect('/signup')

class UserHandler(Handler):
	def get(self):
		username = self.request.get('username')
		self.render('user.html', username=username)

app = webapp2.WSGIApplication([('/signup', Signup),
							('/login', Login),
							('/logout', Logout),
							('/user', UserHandler),
							],
							debug=True)