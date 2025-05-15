import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from app import db

class Resource(db.Model):
    __tablename__ = 'resource'
    id             = db.Column(db.Integer, primary_key=True)
    title          = db.Column(db.String(200), nullable=False)
    description    = db.Column(db.Text)
    filename       = db.Column(db.String(256), nullable=False)
    file_type      = db.Column(db.String(20), nullable=False)             # <-- nouveau
    uploaded_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Catégorie
    category_id    = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category       = db.relationship('Category', back_populates='resources')

    # Qui a uploadé (admin ou auto) et qui a soumis (membre)
    uploaded_by    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploader       = db.relationship('User', foreign_keys=[uploaded_by], back_populates='uploaded_resources')

    submitted_by   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # <-- nouveau
    submitter      = db.relationship('User', foreign_keys=[submitted_by], back_populates='proposed_resources')

    # Workflow de validation
    is_validated   = db.Column(db.Boolean, default=False, nullable=False)            # <-- nouveau

    def save_file(self, file_storage):
        """
        Sauve le fichier dans UPLOAD_FOLDER, met à jour self.filename et self.file_type.
        """
        folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(folder, exist_ok=True)

        # Sécurise et renomme
        name = f"{self.id or 'tmp'}_{secure_filename(file_storage.filename)}"
        path = os.path.join(folder, name)
        file_storage.save(path)
        self.filename  = name

        # Déduction du type à partir de l'extension
        ext = os.path.splitext(file_storage.filename)[1].lstrip('.').lower()
        self.file_type = ext

    @property
    def file_url(self):
        return f"/uploads/{self.filename}"

    def __repr__(self):
        return f'<Resource {self.title!r}, validated={self.is_validated}>'
