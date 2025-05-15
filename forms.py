# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileAllowed, FileRequired

# --- Extensions autorisées (formats Data Science) ---
ALLOWED_EXTENSIONS = {
    'pdf', 'mp4', 'mov', 'csv', 'tsv', 'xlsx', 'ipynb',
    'dta', 'sav', 'sas7bdat', 'rdata', 'json','xml', 'txt',
    'zip', 'tar.gz', 'rar', 'parquet', 'feather','py', 'r',
    'png', 'pptx', 'ppt', 'jpeg', 'xls', 'do'
}

class RegistrationForm(FlaskForm):
    first_name = StringField(
        'Prénom',
        validators=[DataRequired(), Length(min=2, max=64)]
    )
    last_name = StringField(
        'Nom',
        validators=[DataRequired(), Length(min=2, max=64)]
    )
    username = StringField(
        'Nom d’utilisateur',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField(
        'Adresse email',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired(), Length(min=6, max=128)]
    )
    password2 = PasswordField(
        'Confirmez le mot de passe',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("S'inscrire")

class LoginForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

class ResourceForm(FlaskForm):
    title = StringField(
        'Titre',
        validators=[DataRequired(), Length(max=128)]
    )
    description = TextAreaField('Description (facultatif)')
    category = SelectField(
        'Catégorie',
        coerce=int,
        validators=[DataRequired()]
    )
    file = FileField(
        'Fichier (PDF, vidéo, dataset, notebook, etc.)',
        validators=[
            FileRequired(),
            FileAllowed(
                ALLOWED_EXTENSIONS,
                'Extension non autorisée ! Choisissez un fichier parmi : '
                + ', '.join(sorted(ALLOWED_EXTENSIONS))
            )
        ]
    )
    submit = SubmitField('Ajouter la ressource')
