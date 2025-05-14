from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
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
