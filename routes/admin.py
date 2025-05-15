# routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models.user import User
from models.resource import Resource

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Décorateur pour n’autoriser que les admins."""
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapped

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Page d’accueil du back-office admin."""
    # éventuellement passer quelques stats à la template
    total_users = User.query.count()
    pending_users = User.query.filter_by(status='pending').count()
    pending_res = Resource.query.filter_by(is_validated=False).count()
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        pending_users=pending_users,
        pending_res=pending_res
    )

#
# Validation des utilisateurs
#
@bp.route('/validate-users')
@login_required
@admin_required
def validate_users():
    """Liste des comptes en attente d’activation."""
    pending = User.query.filter_by(status='pending').all()
    return render_template('admin/validate_users.html', pending=pending)

@bp.route('/validate-users/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def validate_user(user_id):
    """Active un compte membre."""
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    flash(f"Compte de {user.first_name} {user.last_name} ({user.username}) activé.", 'success')
    return redirect(url_for('admin.validate_users'))

#
# Validation des ressources soumises
#
@bp.route('/pending-resources')
@login_required
@admin_required
def pending_resources():
    """Liste des ressources en attente de validation."""
    resources = Resource.query.filter_by(is_validated=False).order_by(Resource.uploaded_at.desc()).all()
    return render_template('admin/pending_resources.html', resources=resources)

@bp.route('/pending-resources/<int:res_id>/validate', methods=['POST'])
@login_required
@admin_required
def validate_resource(res_id):
    """Valide une ressource et octroie un point à son auteur."""
    res = Resource.query.get_or_404(res_id)
    res.is_validated = True
    if res.submitted_by:
        user = User.query.get(res.submitted_by)
        user.points = (user.points or 0) + 1
    db.session.commit()
    flash(f"Ressource « {res.title} » validée.", 'success')
    return redirect(url_for('admin.pending_resources'))

@bp.route('/pending-resources/<int:res_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_resource(res_id):
    """Rejette et supprime une ressource."""
    res = Resource.query.get_or_404(res_id)
    title = res.title
    db.session.delete(res)
    db.session.commit()
    flash(f"Ressource « {title} » rejetée et supprimée.", 'warning')
    return redirect(url_for('admin.pending_resources'))
