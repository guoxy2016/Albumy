from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(254), unique=True, index=True)
    username = db.Column(db.String(20), unique=True, index=True)
    _password_hash = db.Column(db.String(128))
    website = db.Column(db.String(255))
    bio = db.Column(db.String(120))
    location = db.Column(db.String(50))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, value):
        self._password_hash = generate_password_hash(value)

    def validate_password(self, password):
        return check_password_hash(self._password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username
