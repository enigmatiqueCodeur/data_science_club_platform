from datetime import datetime
from app import db

class ForumCategory(db.Model):
    __tablename__ = 'forum_category'

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(64), unique=True, nullable=False)
    threads = db.relationship('Thread', back_populates='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'

class Thread(db.Model):
    __tablename__ = 'thread'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_category.id'), nullable=False)
    created_by  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    category    = db.relationship('ForumCategory', back_populates='threads')
    author      = db.relationship('User',          back_populates='threads')
    posts       = db.relationship('Post',          back_populates='thread', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Thread {self.title}>'

class Post(db.Model):
    __tablename__ = 'post'

    id          = db.Column(db.Integer, primary_key=True)
    body        = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    author_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    thread_id   = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    parent_id   = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    is_solution = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, nullable=True)


    author   = db.relationship('User', back_populates='posts')
    thread   = db.relationship('Thread', back_populates='posts')
    replies  = db.relationship('Post',
                backref=db.backref('parent', remote_side=[id]),
                cascade='all, delete-orphan')
    reactions = db.relationship('PostReaction', back_populates='post', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Post {self.id} in Thread {self.thread_id}>'

class PostReaction(db.Model):
    __tablename__ = 'post_reaction'

    id            = db.Column(db.Integer, primary_key=True)
    post_id       = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reaction_type = db.Column(db.String(20), default='like')

    post = db.relationship('Post', back_populates='reactions')
    user = db.relationship('User')

    def __repr__(self):
        return f'<Reaction {self.reaction_type} by {self.user_id} on {self.post_id}>'

class Notification(db.Model):
    __tablename__ = 'notification'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message    = db.Column(db.String(200), nullable=False)
    link       = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read    = db.Column(db.Boolean, default=False)

    user = db.relationship('User')

    def __repr__(self):
        return f'<Notification to {self.user_id}: {self.message}>'
