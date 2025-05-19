from datetime import datetime
from app import db

class ResourceAccess(db.Model):
    __tablename__ = 'resource_access'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    action      = db.Column(db.String(20), nullable=False)  # 'view' ou 'download'
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user     = db.relationship('User',     back_populates='accesses')
    resource = db.relationship('Resource', back_populates='accesses')

    def __repr__(self):
        return f'<Access {self.action} by {self.user_id} on {self.resource_id}>'
