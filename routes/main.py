from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from forms import ContactForm
from datetime import date, timedelta
from app import db
from models.resource import Resource
from models.forum_models import Thread, Post
from models.user_session import UserSession
from models.resource_access import ResourceAccess
from models.event import Event
from datetime import datetime
from config import Config
from flask_mail import Mail
from flask import flash, redirect, url_for
from flask_mail import Message

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    recent_resources = Resource.query.filter_by(is_validated=True).order_by(Resource.uploaded_at.desc()).limit(3).all()
    return render_template('index.html', recent_resources=recent_resources)

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    total_views = ResourceAccess.query.filter_by(user_id=current_user.id, action='view').count()
    total_downloads = ResourceAccess.query.filter_by(user_id=current_user.id, action='download').count()
    total_submitted = Resource.query.filter_by(submitted_by=current_user.id).count()
    total_validated = Resource.query.filter_by(uploaded_by=current_user.id).count()
    total_threads = Thread.query.filter_by(created_by=current_user.id).count()
    total_posts = Post.query.filter_by(author_id=current_user.id).count()
    total_points = current_user.points or 0
    sessions = UserSession.query.filter_by(user_id=current_user.id).all()
    mins = [(s.end_time - s.start_time).total_seconds()/60 for s in sessions if s.end_time]
    avg_global = round(sum(mins)/len(mins), 1) if mins else 0
    kpi_cards = [
        {'title': 'Vues totales', 'value': total_views},
        {'title': 'Téléchargements totaux', 'value': total_downloads},
        {'title': 'Ressources proposées', 'value': total_submitted},
        {'title': 'Ressources validées', 'value': total_validated},
        {'title': 'Fils créés', 'value': total_threads},
        {'title': 'Posts rédigés', 'value': total_posts},
        {'title': 'Points XP', 'value': total_points},
        {'title': 'Durée moyenne/session', 'value': f"{avg_global} min"},
    ]
    return render_template('user/dashboard.html', kpi_cards=kpi_cards)

@bp.route('/dashboard/metrics')
@login_required
def dashboard_metrics():
    today = date.today()
    labels, views, downloads, avg_durations = [], [], [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        labels.append(day.strftime('%d/%m'))
        v = ResourceAccess.query.filter_by(
                user_id=current_user.id, action='view'
            ).filter(
                ResourceAccess.timestamp>=day,
                ResourceAccess.timestamp<next_day
            ).count()
        d = ResourceAccess.query.filter_by(
                user_id=current_user.id, action='download'
            ).filter(
                ResourceAccess.timestamp>=day,
                ResourceAccess.timestamp<next_day
            ).count()
        views.append(v)
        downloads.append(d)
        sessions = UserSession.query.filter(
            UserSession.user_id==current_user.id,
            UserSession.start_time>=day,
            UserSession.start_time<next_day
        ).all()
        mins = [(s.end_time - s.start_time).total_seconds()/60 for s in sessions if s.end_time]
        avg = round(sum(mins)/len(mins), 1) if mins else 0
        avg_durations.append(avg)
    return jsonify({
        'labels': labels,
        'views': views,
        'downloads': downloads,
        'avg_durations': avg_durations
    })

@bp.route('/dashboard/contrib')
@login_required
def dashboard_contrib():
    proposed = Resource.query.filter_by(submitted_by=current_user.id).count()
    validated = Resource.query.filter_by(uploaded_by=current_user.id).count()
    return jsonify({
        'labels': ['Proposées', 'Validées'],
        'counts': [proposed, validated]
    })

@bp.route('/dashboard/catdist')
@login_required
def dashboard_catdist():
    from models.category import Category
    cats = Category.query.order_by(Category.name).all()
    labels = [c.name for c in cats]
    counts = [Resource.query.filter_by(category_id=c.id, is_validated=True).count() for c in cats]
    return jsonify({'labels': labels, 'counts': counts})

@bp.route('/evenements')
def list_events():
    upcoming = Event.query.filter(Event.start_time >= datetime.now()).all()
    past = Event.query.filter(Event.start_time < datetime.now()).all()
    return render_template('events/list.html', upcoming=upcoming, past=past)

@bp.route('/contact', methods=['GET','POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(subject=f"[Contact] {form.subject.data}",
                      sender=Config.MAIL_USERNAME,
                      recipients=['admin@votre-domaine.com'])
        mail = Mail()
        msg.body = f"""
De : {form.name.data} <{form.email.data}>

Sujet : {form.subject.data}

Message :
{form.message.data}
"""
        mail.send(msg)
        flash("Votre message a bien été envoyé, merci !", "success")
        return redirect(url_for('main.index'))
    return render_template('contact.html', form=form)