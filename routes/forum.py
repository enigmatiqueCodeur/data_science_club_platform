from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
)
from flask_login import login_required, current_user
from markupsafe import Markup
from app import db, socketio
from models.forum_models import ForumCategory, Thread, Post, PostReaction, Notification
from models.user import User
from forms import ThreadForm, PostForm, EditPostForm
import re
from flask_socketio import emit
from datetime import datetime
import logging  # Ajout pour le logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('forum', __name__, url_prefix='/forum')

def linkify_tags(text):
    """Transforme les @username en liens vers leur profil."""
    if not text:  # Vérifier si le texte est None ou vide
        return ""
    
    def repl(m):
        username = m.group(1)
        link = url_for('user.profile', username=username)
        return f'<a href="{link}">@{username}</a>'
    
    return Markup(re.sub(r'@(\w+)', repl, text))

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)

    query = Thread.query
    if q:
        query = query.filter(Thread.title.ilike(f'%{q}%'))

    pagination = query.order_by(Thread.created_at.desc()) \
                     .paginate(page=page, per_page=10, error_out=False)
    threads = pagination.items
    categories = ForumCategory.query.order_by(ForumCategory.name).all()

    return render_template('forum/index.html',
        categories=categories,
        threads=threads,
        pagination=pagination,
        q=q
    )

@bp.route('/category/<int:cat_id>')
@login_required
def view_category(cat_id):
    category = ForumCategory.query.get_or_404(cat_id)
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str)

    query = Thread.query.filter_by(category_id=cat_id)
    if q:
        query = query.filter(Thread.title.ilike(f'%{q}%'))

    pagination = query.order_by(Thread.created_at.desc()) \
                     .paginate(page=page, per_page=10, error_out=False)

    return render_template('forum/category.html',
        category=category,
        threads=pagination.items,
        pagination=pagination,
        q=q
    )

@bp.route('/thread/new', methods=['GET', 'POST'])
@login_required
def new_thread():
    form = ThreadForm()
    form.category.choices = [
        (c.id, c.name) for c in ForumCategory.query.order_by(ForumCategory.name)
    ]
    if form.validate_on_submit():
        # Log du contenu soumis pour débogage
        logger.info(f"Création d'un nouveau thread: Titre={form.title.data}, Contenu={form.body.data[:50]}...")
        
        try:
            th = Thread(
                title=form.title.data,
                category_id=form.category.data,
                created_by=current_user.id
            )
            db.session.add(th)
            db.session.flush()

            # Vérifier si le body est vide
            if not form.body.data:
                flash("Le contenu du message ne peut pas être vide", "danger")
                return render_template('forum/thread_form.html', form=form)

            body_html = linkify_tags(form.body.data)
            p = Post(
                body=body_html,
                author_id=current_user.id,
                thread_id=th.id
            )
            db.session.add(p)

            current_user.points = (current_user.points or 0) + 5  # +5 XP
            db.session.commit()

            flash("Fil créé ! (+5 XP)", "success")
            return redirect(url_for('forum.view_thread', thread_id=th.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création du thread: {str(e)}")
            flash(f"Une erreur est survenue lors de la création du fil", "danger")
            return render_template('forum/thread_form.html', form=form)

    return render_template('forum/thread_form.html', form=form)

@bp.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def view_thread(thread_id):
    th = Thread.query.get_or_404(thread_id)
    form = PostForm()
    
    if request.method == 'POST':
        logger.info(f"Soumission d'une réponse: content={request.form.get('body', '')[:50]}...")
        
    if form.validate_on_submit():
        try:
            # Vérifier si le corps est vide
            if not form.body.data or form.body.data.strip() == "":
                flash("Le contenu du message ne peut pas être vide", "danger")
                return render_template('forum/thread.html', thread=th, form=form, now=datetime.utcnow())
            
            body_html = linkify_tags(form.body.data)
            p = Post(
                body=body_html,
                author_id=current_user.id,
                thread_id=thread_id,
                parent_id=form.parent_id.data or None
            )
            db.session.add(p)
            db.session.flush()  # Pour obtenir l'ID de p avant le commit

            # Gestion des notifications
            content = form.body.data
            thread_link = url_for('forum.view_thread', thread_id=th.id, _external=True) + f"#post-{p.id}"
            if '@all' in content:
                participants = {post.author for post in th.posts if post.author_id != current_user.id}
                for user in participants:
                    notification = Notification(
                        user_id=user.id,
                        message=f"{current_user.username} a mentionné tout le monde dans '{th.title}'",
                        link=thread_link
                    )
                    db.session.add(notification)
                    socketio.emit('notification', {
                        'message': notification.message,
                        'link': notification.link
                    }, room=f'user_{user.id}')
            elif '@' in content:
                words = content.split()
                mentioned_usernames = [word[1:] for word in words if word.startswith('@') and word != '@all']
                mentioned_users = User.query.filter(User.username.in_(mentioned_usernames)).all()
                for user in mentioned_users:
                    notification = Notification(
                        user_id=user.id,
                        message=f"{current_user.username} vous a mentionné dans '{th.title}'",
                        link=thread_link
                    )
                    db.session.add(notification)
                    socketio.emit('notification', {
                        'message': notification.message,
                        'link': notification.link
                    }, room=f'user_{user.id}')

            current_user.points = (current_user.points or 0) + 2  # +2 XP
            db.session.commit()

            flash("Réponse ajoutée ! (+2 XP)", "success")
            return redirect(
                url_for('forum.view_thread', thread_id=thread_id) + f"#post-{p.id}"
            )
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur lors de l'ajout de la réponse: {str(e)}")
            flash("Une erreur est survenue lors de l'ajout de votre réponse", "danger")
    elif request.method == 'POST':
        # Si le formulaire a été soumis mais n'a pas été validé
        logger.error(f"Erreurs de validation du formulaire: {form.errors}")
        flash("Veuillez vérifier les informations saisies", "warning")

    return render_template('forum/thread.html', thread=th, form=form, now=datetime.utcnow())

@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        abort(403)
    form = EditPostForm(body=post.body)
    if form.validate_on_submit():
        post.body = linkify_tags(form.body.data)
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Post mis à jour !", "success")
        return redirect(url_for('forum.view_thread', thread_id=post.thread_id) + f"#post-{post.id}")
    return render_template('forum/edit_post.html', form=form, post=post)

@bp.route('/post/<int:post_id>/mark_solution', methods=['POST'])
@login_required
def mark_solution(post_id):
    post = Post.query.get_or_404(post_id)
    thread = post.thread
    if thread.created_by != current_user.id:
        abort(403)
    for p in thread.posts:
        p.is_solution = False
    post.is_solution = True
    db.session.commit()
    flash("Post marqué comme solution !", "success")
    return redirect(url_for('forum.view_thread', thread_id=thread.id) + f"#post-{post.id}")

@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    reaction = PostReaction.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if reaction:
        db.session.delete(reaction)
        action = 'unlike'
    else:
        reaction = PostReaction(post_id=post_id, user_id=current_user.id)
        db.session.add(reaction)
        action = 'like'
    db.session.commit()
    return jsonify({'action': action, 'count': len(post.reactions)})

@bp.route('/users', methods=['GET'])
@login_required
def get_users():
    query = request.args.get('q', '')
    users = User.query.filter(User.username.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{'username': user.username} for user in users])

@bp.route('/notifications')
@login_required
def notifications():
    filter_type = request.args.get('filter', 'all')
    query = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc())
    if filter_type == 'unread':
        query = query.filter_by(is_read=False)
    elif filter_type == 'all':
        pass  # Pas de filtre supplémentaire pour "all"
    notifications = query.paginate(page=request.args.get('page', 1, type=int), per_page=10, error_out=False).items
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template('forum/notifications.html', notifications=notifications, unread_count=unread_count, filter_type=filter_type)

@bp.route('/notification/<int:notif_id>/mark_read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notification = Notification.query.get_or_404(notif_id)
    if notification.user_id != current_user.id:
        abort(403)
    notification.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'})

# Route de débogage pour tester le contenu du formulaire
@bp.route('/debug/form', methods=['POST'])
@login_required
def debug_form():
    """Route temporaire pour déboguer les soumissions de formulaire"""
    form_data = {key: request.form.get(key) for key in request.form}
    logger.info(f"Données de formulaire reçues: {form_data}")
    return jsonify({"status": "debug", "form_data": form_data})