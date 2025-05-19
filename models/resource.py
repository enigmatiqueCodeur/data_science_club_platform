import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from app import db

class Resource(db.Model):
    __tablename__ = 'resource'

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text)
    filename      = db.Column(db.Text, nullable=False)
    file_type     = db.Column(db.Text, nullable=False)
    uploaded_at   = db.Column(db.DateTime, default=datetime.utcnow)
    views         = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    category_id   = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    uploaded_by   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    submitted_by  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_validated  = db.Column(db.Boolean, default=False, nullable=False)

    accesses      = db.relationship('ResourceAccess', back_populates='resource', lazy='dynamic')
    category      = db.relationship('Category',       back_populates='resources')
    uploader      = db.relationship('User', foreign_keys=[uploaded_by], back_populates='uploaded_resources')
    submitter     = db.relationship('User', foreign_keys=[submitted_by], back_populates='proposed_resources')

    @property
    def downloads(self):
        return self.accesses.filter_by(action='download').count()

    @property
    def file_url(self):
        return f"/uploads/{self.filename}"

    @property
    def filesize(self):
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], self.filename)
        try:
            return os.path.getsize(path)
        except OSError:
            return 0

    @property
    def filesize_human(self):
        size = self.filesize
        for unit in ['B','KB','MB','GB','TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"

    def __repr__(self):
        return f'<Resource {self.title!r} (views={self.views})>'
