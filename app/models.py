from datetime import datetime as dt
from flask.ext.login import UserMixin
from simplecrypt import encrypt
from config import SECRET_KEY
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from app import db, login_manager

##################################################
# Tables (for many-to-many relationships)
##################################################


						   
##################################################
# Models
# These should inherit from db.Model if they have an associated table
##################################################

class User(db.Model, UserMixin):
	"""Represents a user."""
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	email = db.Column(db.String(128), unique=True)
	password = db.Column(db.LargeBinary(4096))
	
	# This is a list of characters designating what permissions the user has:
	# a: admin, etc.
	permissions = db.Column(db.String(64))
	
	# This is a list of metadata tags useful for filtering; for example, class, year, major, etc.
	metadata_str = db.Column(db.LargeBinary(4096))

	def __init__(self, name, password, email):
		self.name = name
		self.password = encrypt(SECRET_KEY, password)
		self.email = email
		self.permissions = ""
		self.metadata_str = ""


##################################################
# Helper functions
##################################################
	
# We need one of these
@login_manager.user_loader
def get_user(id=None, name=None, email=None):
	if id:
		return User.query.filter_by(id=int(id)).first()
	if name:
		return User.query.filter_by(name=name).first()
	if email:
		return User.query.filter_by(email=email).first()
	return None
	

	
	

