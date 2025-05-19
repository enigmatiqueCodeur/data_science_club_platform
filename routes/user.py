from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from models import Resource, Thread, Post
from sqlalchemy import func
from app import db
from models.forum_models import  Thread, Post
from models.user import User
from models.resource_access import ResourceAccess
from forms import ProfileForm, ChangePasswordForm
from datetime import datetime
from flask import flash, redirect, url_for
from werkzeug.utils import secure_filename
import os



bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Statistiques globales
    total_threads = Thread.query.filter_by(created_by=current_user.id).count()
    total_posts   = Post.query.filter_by(author_id=current_user.id).count()
    total_subs    = Resource.query.filter_by(submitted_by=current_user.id).count()
    total_uploads = Resource.query.filter_by(uploaded_by=current_user.id).count()

    # Évolution mensuelle des posts (les 6 derniers mois)
    posts_per_month = (
        db.session.query(
            func.date_trunc('month', Post.created_at).label('month'),
            func.count(Post.id).label('count')
        )
        .filter(Post.author_id==current_user.id)
        .group_by('month')
        .order_by('month')
        .all()
    )
    # Pareil pour les ressources soumises
    subs_per_month = (
        db.session.query(
            func.date_trunc('month', Resource.created_at).label('month'),
            func.count(Resource.id).label('count')
        )
        .filter(Resource.submitted_by==current_user.id)
        .group_by('month')
        .order_by('month')
        .all()
    )

    return render_template('user/dashboard.html',
        total_threads=total_threads,
        total_posts=total_posts,
        total_subs=total_subs,
        total_uploads=total_uploads,
        posts_per_month=posts_per_month,
        subs_per_month=subs_per_month
    )

@bp.route('/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # KPI
    stats = {
      'views': ResourceAccess.query.filter_by(user_id=user.id, action='view').count(),
      'downloads': ResourceAccess.query.filter_by(user_id=user.id, action='download').count(),
      'threads': Thread.query.filter_by(created_by=user.id).count(),
      'posts': Post.query.filter_by(author_id=user.id).count(),
    }
    # Activité récente (derniers 10 évènements ressources ou forum)
    recent_views = ResourceAccess.query.filter_by(user_id=user.id).order_by(ResourceAccess.timestamp.desc()).limit(5)
    recent_posts = Post.query.filter_by(author_id=user.id).order_by(Post.created_at.desc()).limit(5)
    # Fusionner et trier
    recent_activity = sorted(
      [ { 'timestamp': r.timestamp, 'description': f"Vu ressource {r.resource.title}" } for r in recent_views ] +
      [ { 'timestamp': p.created_at,  'description': f"Posté dans «{p.thread.title}»" } for p in recent_posts ],
      key=lambda x: x['timestamp'], reverse=True
    )[:10]
    return render_template(
      'user/profile.html',
      user=user,
      stats=stats,
      recent_activity=recent_activity
    )


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.bio = form.bio.data
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            filepath = os.path.join('static/uploads/avatars', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            form.avatar.data.save(filepath)
            current_user.avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')
        current_user.last_online = datetime.utcnow()
        db.session.commit()
        flash("Profil mis à jour.", "success")
        return redirect(url_for('user.profile', username=current_user.username))
    return render_template('user/edit_profile.html', form=form)


@bp.route('/change_password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash("Mot de passe actuel invalide.", "danger")
        else:
            current_user.set_password(form.password.data)
            db.session.commit()
            flash("Mot de passe modifié.", "success")
            return redirect(url_for('user.profile', username=current_user.username))
    return render_template('user/change_password.html', form=form)

