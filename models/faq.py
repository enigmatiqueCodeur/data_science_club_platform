from app import db

class Faq(db.Model):
    __tablename__ = 'faq'
    id       = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), unique=True, nullable=False)
    answer   = db.Column(db.Text, nullable=False)
