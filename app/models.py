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


# Many to Many Relationship between events and users
relationships  = db.Table('relations',
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_private = db.Column(db.Boolean)
    manager_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    tasks = db.relationship('Task', backref='event',
                                lazy='dynamic')
    # Define relationship for many to many table
    users = db.relationship('Users', secondary=relationships,
        backref=db.backref('events', lazy='dynamic'))





class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    location = db.Column(db.String(128))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    users = db.relationship('User', lazy='dynamic')
    description = db.Column(db.String(512))



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
