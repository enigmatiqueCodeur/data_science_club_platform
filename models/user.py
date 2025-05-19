from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True)
    payment_code  = db.Column(db.String(20), unique=True, nullable=True)
    first_name    = db.Column(db.String(64), nullable=False)
    last_name     = db.Column(db.String(64), nullable=False)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role          = db.Column(db.String(10), default='member', nullable=False)
    status        = db.Column(db.String(10), default='pending', nullable=False)
    points        = db.Column(db.Integer, default=0, nullable=False)
    bio           = db.Column(db.Text, nullable=True)
    last_online   = db.Column(db.DateTime, nullable=True)
    avatar_url    = db.Column(db.String(256), nullable=True)

    # Relations
    threads            = db.relationship('Thread',        back_populates='author',        cascade='all, delete-orphan')
    posts              = db.relationship('Post',          back_populates='author',        cascade='all, delete-orphan')
    uploaded_resources = db.relationship('Resource',      back_populates='uploader',      foreign_keys='Resource.uploaded_by')
    proposed_resources = db.relationship('Resource',      back_populates='submitter',     foreign_keys='Resource.submitted_by')
    sessions           = db.relationship('UserSession',   back_populates='user',         cascade='all, delete-orphan')
    accesses           = db.relationship('ResourceAccess', back_populates='user',         lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
