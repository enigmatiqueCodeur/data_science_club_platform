# manage.py
from flask.cli       import FlaskGroup
from app              import create_app, db
from flask_migrate    import Migrate, upgrade

app     = create_app()
migrate = Migrate(app, db)           # ← c’est l’appel clé
cli     = FlaskGroup(create_app=create_app)

@cli.command("deploy")
def deploy():
    """Applique les migrations en base."""
    upgrade()

if __name__ == "__main__":
    cli()
