from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.user import User

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Décorateur pour n’autoriser que les admins."""
    from functools import wraps
    from flask import abort
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapped

@bp.route('/validate-users')
@login_required
@admin_required
def validate_users():
    # Récupère tous les utilisateurs en attente
    pending = User.query.filter_by(status='pending').all()
    return render_template('admin/validate_users.html', pending=pending)

@bp.route('/validate-users/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def validate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    flash(f"Compte de {user.first_name} {user.last_name} ({user.username}) activé.", 'success')
    return redirect(url_for('admin.validate_users'))
