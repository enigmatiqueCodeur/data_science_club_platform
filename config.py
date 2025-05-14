import os
from dotenv import load_dotenv

# Charge .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']

    # Si tu définis aussi DATABASE_URL, tu peux le prioriser :
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Construire sans password dans l'URL :
        user = os.environ.get('PGUSER', 'postgres')
        host = os.environ.get('PGHOST', 'localhost')
        port = os.environ.get('PGPORT', '5432')
        dbname = os.environ.get('PGDATABASE', 'club_db')
        SQLALCHEMY_DATABASE_URI = f"postgresql://{user}@{host}:{port}/{dbname}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
