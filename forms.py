from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField,
    TextAreaField, SelectField, SubmitField, HiddenField
)
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import StringField, TextAreaField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Optional
from config import Config

class RegistrationForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired(), Length(2,64)])
    last_name  = StringField('Nom',     validators=[DataRequired(), Length(2,64)])
    username   = StringField('Nom d’utilisateur', validators=[DataRequired(), Length(3,64)])
    email      = StringField('Adresse email',      validators=[DataRequired(), Email(), Length(max=120)])
    password   = PasswordField('Mot de passe',      validators=[DataRequired(), Length(6,128)])
    password2  = PasswordField('Confirmez le mot de passe',
                               validators=[DataRequired(), EqualTo('password')])
    submit     = SubmitField("S'inscrire")

class LoginForm(FlaskForm):
    username    = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password    = PasswordField('Mot de passe',     validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit      = SubmitField('Connexion')

class ResourceForm(FlaskForm):
    title       = StringField('Titre',       validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description (facultatif)')
    category    = SelectField('Catégorie',  coerce=int, validators=[DataRequired()])
    file        = FileField('Fichier', validators=[
        FileRequired(),
        FileAllowed(Config.ALLOWED_EXTENSIONS,
                    'Extension non autorisée.')
    ])
    submit      = SubmitField('Valider')


class ThreadForm(FlaskForm):
    title    = StringField('Titre du fil', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Catégorie', coerce=int, validators=[DataRequired()])
    body     = TextAreaField('Message initial', validators=[DataRequired(), Length(min=5)])
    submit   = SubmitField('Créer')

class PostForm(FlaskForm):
    body      = TextAreaField('Votre message', validators=[DataRequired(), Length(min=1)])
    parent_id = HiddenField()  
    submit    = SubmitField('Envoyer')


class CategoryForm(FlaskForm):
    name   = StringField('Nom de la catégorie', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Enregistrer')


class ProfileForm(FlaskForm):
    bio        = TextAreaField('Bio', validators=[Length(max=500)])
    avatar     = FileField('Nouvel avatar', validators=[FileAllowed(['jpg','png','gif'])])
    submit     = SubmitField('Enregistrer')


class EditPostForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Mettre à jour')


class EventForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_time = DateTimeField('Début (format: AAAA-MM-JJ HH:MM)', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('Fin (optionnel)', format='%Y-%m-%d %H:%M', validators=[Optional()])
    location = StringField('Lieu')
    is_online = BooleanField('Événement en ligne')
    max_attendees = IntegerField('Nombre max de participants (optionnel)', validators=[Optional()])

class ForgotPasswordForm(FlaskForm):
    email = StringField("Adresse email", validators=[DataRequired(), Email()])
    submit = SubmitField("Envoyer le lien")

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        "Nouveau mot de passe",
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo('new_password')]
    )
    submit = SubmitField("Changer le mot de passe")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Mot de passe actuel",
        validators=[DataRequired(message="Obligatoire")]
    )
    new_password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            DataRequired(message="Obligatoire"),
            Length(min=6, message="Doit contenir au moins 6 caractères")
        ]
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[
            DataRequired(message="Obligatoire"),
            EqualTo('new_password', message="Les mots de passe doivent correspondre")
        ]
    )
    submit = SubmitField("Modifier le mot de passe")
    
class ContactForm(FlaskForm):
    name    = StringField("Nom", validators=[DataRequired()])
    email   = StringField("Email", validators=[DataRequired(), Email()])
    subject = StringField("Sujet", validators=[DataRequired(), Length(max=128)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])
    submit  = SubmitField("Envoyer")

class ResourceCategoryForm(FlaskForm):
    name = StringField(
        'Nom de la catégorie', 
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField('Enregistrer')