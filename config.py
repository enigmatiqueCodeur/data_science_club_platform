import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    MAIL_SECRET_KEY = os.environ.get('SECRET_KEY')

    # BDD
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        user    = os.environ.get('PGUSER', 'postgres')
        host    = os.environ.get('PGHOST', 'localhost')
        port    = os.environ.get('PGPORT', '5432')
        dbname  = os.environ.get('PGDATABASE', 'club_db')
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{user}@{host}:{port}/{dbname}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads', 'resources')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'mp4', 'mov', 'csv', 'tsv', 'xlsx', 'ipynb',
    'dta', 'sav', 'sas7bdat', 'rdata', 'json','xml', 'txt',
    'zip', 'tar.gz', 'rar', 'parquet', 'feather','py', 'r',
    'png', 'pptx', 'ppt', 'jpeg', 'jpg', 'xls', 'do'}


    # Flask-Mail
    MAIL_SERVER   = 'smtp.gmail.com'
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USE_SSL  = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('ENSEA Data Science Club', MAIL_USERNAME)