# routes/auth.py
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from urllib.parse import urlparse
from datetime import date

from app import db
from models.user import User
from forms import RegistrationForm

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Création du membre en status pending, role member
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            role='member',
            status='pending'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # pour récupérer user.id

        # Génération du code de paiement
        code = f"EDSC{date.today().year}-{user.id:04d}"
        user.payment_code = code
        db.session.commit()

        return render_template(
            'register_success.html',
            payment_code=code,
            first_name=user.first_name,
            last_name=user.last_name
        )

    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # Page qui contient le JS pour /check-email & /login-json
    return render_template('login.html')


@bp.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    return jsonify({
        'exists': bool(user),
        'status': user.status if user else None,
        'role':   user.role   if user else None
    })


@bp.route('/login-json', methods=['POST'])
def login_json():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    # Vérification mot de passe et statut
    if not user or not user.check_password(data.get('password')):
        return jsonify(success=False, message="Identifiants invalides.")
    if user.status != 'active':
        return jsonify(success=False, message="Compte non activé.")

    # Connexion
    login_user(user)

    # Redirection selon le rôle
    if user.role == 'admin':
        redirect_to = url_for('admin.validate_users')
    else:
        redirect_to = url_for('main.index')
    return jsonify(success=True, redirect=redirect_to)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))
