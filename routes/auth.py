# routes/auth.py
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, jsonify, session
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from urllib.parse import urlparse as url_parse
from datetime import date, datetime
from flask import current_app
from app import db
from models.user import User
# Nouveau modèle pour tracker les sessions
from models.user_session import UserSession
from forms import RegistrationForm, LoginForm
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from forms import ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm


bp = Blueprint('auth', __name__)



mail = Mail()


@bp.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='pwd-reset')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message("Réinitialisation de votre mot de passe",
                          recipients=[user.email])
            msg.body = f"Pour réinitialiser votre mot de passe, cliquez ici :\n{reset_url}\n\n" \
                       "Ce lien expire dans 30 minutes."
            mail.send(msg)
        flash("Si cette adresse existe, vous allez recevoir un email de réinitialisation.", "info")
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', form=form)

@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='pwd-reset', max_age=1800)
    except:
        flash("Le lien est invalide ou expiré.", "danger")
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Votre mot de passe a bien été changé.", "success")
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Vérifier l’ancien mot de passe :
        if not current_user.check_password(form.current_password.data):
            flash("Mot de passe actuel incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Mot de passe mis à jour !", "success")
            return redirect(url_for('main.dashboard'))
    return render_template('change_password.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
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
        db.session.flush()
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


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data) or user.status!='active':
            flash('Login invalide ou compte non activé.', 'danger')
        else:
            # connexion Flask-Login
            login_user(user, remember=form.remember_me.data)

            # ==== Nouveau : on démarre la session en base ====
            us = UserSession(user_id=user.id, start_time=datetime.utcnow())
            db.session.add(us)
            db.session.commit()
            # on stocke l'id pour le fermer au logout
            session['user_session_id'] = us.id

            # redirection
            next_page = request.form.get('next') or request.args.get('next')
            if not next_page or url_parse(next_page).netloc:
                next_page = url_for('main.index')
            return redirect(next_page)

    return render_template('login.html', form=form)


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
    if not user or not user.check_password(data.get('password')):
        return jsonify(success=False, message="Identifiants invalides.")
    if user.status != 'active':
        return jsonify(success=False, message="Compte non activé.")
    login_user(user)
    # Pas de session JSON track pour l'instant
    if user.role == 'admin':
        redirect_to = url_for('admin.dashboard')
    else:
        redirect_to = url_for('main.index')
    return jsonify(success=True, redirect=redirect_to)


@bp.route('/logout')
@login_required
def logout():
    # ==== Nouveau : on clôt la session en base ====
    sid = session.pop('user_session_id', None)
    if sid:
        us = UserSession.query.get(sid)
        if us and us.end_time is None:
            us.end_time = datetime.utcnow()
            db.session.commit()
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))
