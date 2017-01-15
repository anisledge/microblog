import webapp2 

class Handler(webapp2.RequestHandler):
	def render(self, string):
		self.response.out.write(string)

class Signup(Handler):
	def get(self):
		self.render('User signup')

	def post(self):
		pass

class Login(Handler):
	def get(self):
		self.render('User login')

	def post(self):
		pass

class Logout(Handler):
	def get(self):
		self.render('User logout')

class UserHandler(Handler):
	def get(self):
		self.render('User home')

app = webapp2.WSGIApplication([('/signup', Signup),
							('/login', Login),
							('/logout', Logout),
							('/user', UserHandler),
							],
							debug=True)