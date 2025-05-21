from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, abort
)
from flask_login import login_required, current_user
from app import db
from models.user import User
from models.resource import Resource
from models.forum_models import ForumCategory
from forms import CategoryForm
from models.event import Event, EventAttendance
from forms import EventForm  
from datetime import datetime
from models.category import Category  
from forms import ResourceCategoryForm


bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.role=='admin'):
            abort(403)
        return f(*args, **kwargs)
    return wrapped

@bp.route('/')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')

# Valider membres
@bp.route('/validate-users')
@login_required
@admin_required
def validate_users():
    pending = User.query.filter_by(status='pending').all()
    return render_template('admin/validate_users.html', pending=pending)

@bp.route('/validate-users/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def validate_user(user_id):
    u = User.query.get_or_404(user_id)
    u.status = 'active'
    db.session.commit()
    flash(f"Compte {u.username} activé.", 'success')
    return redirect(url_for('admin.validate_users'))

# Valider ressources
@bp.route('/pending-resources')
@login_required
@admin_required
def pending_resources():
    todo = Resource.query.filter_by(is_validated=False).all()
    return render_template('admin/pending_resources.html', resources=todo)

@bp.route('/pending-resources/<int:res_id>/validate', methods=['POST'])
@login_required
@admin_required
def validate_resource(res_id):
    r = Resource.query.get_or_404(res_id)
    r.is_validated = True
    r.uploaded_by = current_user.id  # Admin qui valide
    if r.submitted_by:
        usr = User.query.get(r.submitted_by)
        usr.points = (usr.points or 0) + 50  # +50 XP pour validation
    db.session.commit()
    flash(f"Ressource «{r.title}» validée (+50 XP pour l'utilisateur).", 'success')
    return redirect(url_for('admin.pending_resources'))

@bp.route('/pending-resources/<int:res_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_resource(res_id):
    r = Resource.query.get_or_404(res_id)
    db.session.delete(r)
    db.session.commit()
    flash(f"Ressource «{r.title}» rejetée.", 'warning')
    return redirect(url_for('admin.pending_resources'))

@bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    cats = ForumCategory.query.order_by(ForumCategory.name).all()
    return render_template('admin/categories.html', categories=cats)

@bp.route('/categories/new', methods=['GET','POST'])
@login_required
@admin_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        db.session.add(ForumCategory(name=form.name.data))
        db.session.commit()
        flash("Catégorie ajoutée.", "success")
        return redirect(url_for('admin.manage_categories'))
    return render_template('admin/category_form.html', form=form)

@bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    cat = ForumCategory.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash("Catégorie supprimée.", "warning")
    return redirect(url_for('admin.manage_categories'))

@bp.route('/events')
@login_required
@admin_required
def manage_events():
    upcoming = Event.query.filter(Event.start_time >= datetime.now()).order_by(Event.start_time).all()
    past = Event.query.filter(Event.start_time < datetime.now()).order_by(Event.start_time.desc()).all()
    return render_template('admin/events.html', upcoming=upcoming, past=past)

@bp.route('/events/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            location=form.location.data,
            is_online=form.is_online.data,
            max_attendees=form.max_attendees.data,
            creator_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Événement créé avec succès!', 'success')
        return redirect(url_for('admin.manage_events'))
    return render_template('admin/event_form.html', form=form)

@bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        form.populate_obj(event)
        db.session.commit()
        flash('Événement mis à jour!', 'success')
        return redirect(url_for('admin.manage_events'))
    return render_template('admin/event_form.html', form=form, event=event)

@bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Événement supprimé!', 'warning')
    return redirect(url_for('admin.manage_events'))


@bp.route('/resource-categories')
@login_required
@admin_required
def manage_resource_categories():
    cats = Category.query.order_by(Category.name).all()
    return render_template(
        'admin/resource_categories.html',
        categories=cats
    )

@bp.route('/resource-categories/new', methods=['GET','POST'])
@login_required
@admin_required
def new_resource_category():
    form = ResourceCategoryForm()
    if form.validate_on_submit():
        c = Category(name=form.name.data)
        db.session.add(c)
        db.session.commit()
        flash("Catégorie créée.", "success")
        return redirect(url_for('admin.manage_resource_categories'))
    return render_template(
        'admin/edit_resource_category.html',
        form=form,
        title="Nouvelle catégorie"
    )

@bp.route('/resource-categories/<int:cat_id>/edit', methods=['GET','POST'])
@login_required
@admin_required
def edit_resource_category(cat_id):
    c = Category.query.get_or_404(cat_id)
    form = ResourceCategoryForm(obj=c)
    if form.validate_on_submit():
        c.name = form.name.data
        db.session.commit()
        flash("Catégorie mise à jour.", "success")
        return redirect(url_for('admin.manage_resource_categories'))
    return render_template(
        'admin/edit_resource_category.html',
        form=form,
        title="Modifier catégorie"
    )

@bp.route('/resource-categories/<int:cat_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_resource_category(cat_id):
    c = Category.query.get_or_404(cat_id)
    db.session.delete(c)
    db.session.commit()
    flash("Catégorie supprimée.", "info")
    return redirect(url_for('admin.manage_resource_categories'))