from datetime import datetime
from app import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    location = db.Column(db.String(100))
    is_online = db.Column(db.Boolean, default=False)
    max_attendees = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relations
    creator = db.relationship('User', backref='created_events')
    attendees = db.relationship('User', secondary='event_attendance', backref='events_attending')

class EventAttendance(db.Model):
    __tablename__ = 'event_attendance'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)