from google.appengine.ext import db
 
class User(db.Model):
	username = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	email = db.StringProperty(required = False)

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

	author = db.ReferenceProperty(User, collection_name='posts')

class Like(db.Model):
	author = db.ReferenceProperty(User, collection_name='likes')
	post = db.ReferenceProperty(Post, collection_name='likes')