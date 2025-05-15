from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Blueprints
    from routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from routes.resources import bp as resources_bp
    app.register_blueprint(resources_bp)


    return app
