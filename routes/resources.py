import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request, send_from_directory, current_app, session
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import Category, Resource
from models.resource_access import ResourceAccess
from forms import ResourceForm

bp = Blueprint('resources', __name__, url_prefix='/resources')

@bp.route('/', methods=['GET'])
@login_required
def list_resources():
    q    = request.args.get('q', '', type=str)
    cat  = request.args.get('cat', type=int)
    sort = request.args.get('sort', 'recent', type=str)

    query = Resource.query.join(Category).filter(Resource.is_validated.is_(True))
    if q:
        query = query.filter(Resource.title.ilike(f"%{q}%"))
    if cat:
        query = query.filter(Resource.category_id == cat)

    if sort == 'popular':
        query = query.order_by(Resource.views.desc())
    else:
        query = query.order_by(Resource.uploaded_at.desc())

    resources  = query.all()
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        'resources.html',
        resources=resources,
        categories=categories,
        q=q, cat=cat, sort=sort
    )

@bp.route('/<int:res_id>')
@login_required
def resource_detail(res_id):
    res = Resource.query.get_or_404(res_id)

    key = f"viewed_resource_{res_id}"
    if not session.get(key):
        access = ResourceAccess(user_id=current_user.id,
                                resource_id=res.id,
                                action='view')
        db.session.add(access)
        res.views += 1
        db.session.commit()
        session[key] = True

    return render_template('resource_detail.html', resource=res)

@bp.route('/download/<int:res_id>')
@login_required
def download(res_id):
    res = Resource.query.get_or_404(res_id)

    access = ResourceAccess(user_id=current_user.id,
                            resource_id=res.id,
                            action='download')
    db.session.add(access)
    db.session.commit()

    # Chemin complet du fichier
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], res.filename)
    
    # Vérification que le fichier existe
    if not os.path.exists(file_path):
        flash("Fichier introuvable sur le serveur", 'error')
        return redirect(url_for('resources.list_resources'))

    return send_from_directory(
        directory=current_app.config['UPLOAD_FOLDER'],
        path=res.filename,
        as_attachment=True
    )

@bp.route('/new', methods=['GET','POST'])
@login_required
def upload_resource():
    is_admin = (current_user.role == 'admin')
    form = ResourceForm()
    form.category.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        print("Chemin complet du dossier upload:", current_app.config['UPLOAD_FOLDER'])
        print("Le dossier existe?", os.path.exists(current_app.config['UPLOAD_FOLDER']))
        f    = form.file.data
        orig = secure_filename(f.filename)
        uniq = f"{uuid.uuid4().hex}_{orig}"
        dst  = os.path.join(current_app.config['UPLOAD_FOLDER'], uniq)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        f.save(dst)

        res = Resource(
            title        = form.title.data,
            description  = form.description.data,
            filename     = uniq,
            file_type    = f.mimetype,
            category_id  = form.category.data,
            uploaded_by  = current_user.id if is_admin else None,
            submitted_by = None if is_admin else current_user.id,
            is_validated = is_admin
        )
        db.session.add(res)
        if not is_admin:
            current_user.points = (current_user.points or 0) + 10  # +10 XP pour proposition
        db.session.commit()

        msg = "Ressource ajoutée" if is_admin \
              else "Proposition envoyée, en attente de validation (+10 XP)"
        flash(msg, 'success')
        return redirect(url_for('resources.list_resources'))

    return render_template(
        'resource_form.html',
        form=form,
        is_admin=is_admin
    )

@bp.route('/file/<filename>')
@login_required
def serve_file(filename):
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=False
    )

@bp.route('/edit/<int:res_id>', methods=['GET','POST'])
@login_required
def edit_resource(res_id):
    if current_user.role != 'admin':
        flash("Accès interdit.", 'danger')
        return redirect(url_for('resources.list_resources'))

    res = Resource.query.get_or_404(res_id)
    form = ResourceForm(
        title       = res.title,
        description = res.description,
        category    = res.category_id
    )
    form.category.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        res.title       = form.title.data
        res.description = form.description.data
        res.category_id = form.category.data

        if form.file.data:
            old = os.path.join(current_app.config['UPLOAD_FOLDER'], res.filename)
            if os.path.exists(old):
                os.remove(old)
            f    = form.file.data
            name = f"{uuid.uuid4().hex}_{secure_filename(f.filename)}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], name)
            f.save(path)
            res.filename  = name
            res.file_type = f.mimetype

        db.session.commit()
        flash("Ressource modifiée.", 'success')
        return redirect(url_for('resources.list_resources'))

    return render_template(
        'resource_form.html',
        form=form,
        edit=True,
        resource=res
    )

@bp.route('/delete/<int:res_id>', methods=['POST'])
@login_required
def delete_resource(res_id):
    if current_user.role != 'admin':
        flash("Accès interdit.", 'danger')
        return redirect(url_for('resources.list_resources'))

    res = Resource.query.get_or_404(res_id)
    fp  = os.path.join(current_app.config['UPLOAD_FOLDER'], res.filename)
    if os.path.exists(fp):
        os.remove(fp)

    db.session.delete(res)
    db.session.commit()
    flash("Ressource supprimée.", 'success')
    return redirect(url_for('resources.list_resources'))