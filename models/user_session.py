from datetime import datetime
from app import db

class UserSession(db.Model):
    __tablename__ = 'user_session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time   = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='sessions')

def __repr__(self):
        return f'<Session {self.user_id} from {self.start_time}>'