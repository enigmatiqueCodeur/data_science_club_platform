import os
from flask import Flask, g, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_mail import Mail



db      = SQLAlchemy()
migrate = Migrate()
login   = LoginManager()
login.login_view = 'auth.login'
login.login_message_category = 'warning'
socketio = SocketIO()
mail = Mail()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    mail.init_app(app)

    # import and register models so SQLAlchemy sees them
    from models.user            import User
    from models.forum_models    import ForumCategory, Thread, Post, PostReaction, Notification
    from models.resource        import Resource
    from models.resource_access import ResourceAccess
    from models.user_session    import UserSession

    # user loader for Flask-Login
    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # context processor for e.g. unread notifications
    @app.context_processor
    def inject_unread_count():
        if hasattr(g, 'user') and g.user.is_authenticated:
            count = Notification.query.filter_by(user_id=g.user.id, is_read=False).count()
        else:
            count = 0
        return dict(unread_count=count)
    
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%d/%m/%Y %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)

    # register blueprints
    from routes.main      import bp as main_bp
    from routes.auth      import bp as auth_bp
    from routes.admin     import bp as admin_bp
    from routes.resources import bp as resources_bp
    from routes.forum     import bp as forum_bp
    from routes.user      import bp as user_bp
    from routes.chat import bp as chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,      url_prefix='/auth')
    app.register_blueprint(admin_bp,     url_prefix='/admin')
    app.register_blueprint(resources_bp, url_prefix='/resources')
    app.register_blueprint(forum_bp,     url_prefix='/forum')
    app.register_blueprint(user_bp,      url_prefix='/user')
    app.register_blueprint(chat_bp)

    # ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads/avatars'), exist_ok=True)

    return app
