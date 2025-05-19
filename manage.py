from flask.cli import FlaskGroup
from app import create_app, db, socketio
from flask_migrate import Migrate, upgrade

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(create_app=create_app)

@cli.command("deploy")
def deploy():
    """Applique les migrations en base."""
    upgrade()

if __name__ == "__main__":
    # Utiliser socketio.run pour démarrer l'application avec WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)