import webapp2 

class Handler(webapp2.RequestHandler):
	def render(self, **params):
		self.response.out.write(params)

class Signup(Handler):
	def get(self):
		pass

	def post(self):
		pass

class Login(Handler):
	def get(self):
		pass

	def post(self):
		pass

class Logout(Handler):
	def get(self):
		pass

class UserHandler(Handler):
	def get(self):
		pass

app = webapp2.WSGIApplication([('/signup', Signup),
							('/login', Login),
							('/logout', Logout),
							('/user', UserHandler),
							],
							debug=True)