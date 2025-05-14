from app import create_app, db
from flask_migrate import upgrade

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db}

def deploy():
    """Appelle cette fonction pour migrer la base."""
    upgrade()
