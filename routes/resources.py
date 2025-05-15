# routes/resources.py
import os, uuid
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    request, send_from_directory, current_app, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from models import Category, Resource
from forms import ResourceForm
from routes.admin import admin_required  # récupère ton décorateur

bp = Blueprint('resources', __name__, url_prefix='/resources')


# 1. LISTE & FILTRAGE (seulement les ressources validées)
@bp.route('/', methods=['GET'])
@login_required
def list_resources():
    q   = request.args.get('q', '', type=str)
    cat = request.args.get('cat', type=int)

    query = Resource.query \
        .join(Category) \
        .filter(Resource.is_validated.is_(True))

    if q:
        query = query.filter(Resource.title.ilike(f'%{q}%'))
    if cat:
        query = query.filter(Resource.category_id == cat)

    resources  = query.order_by(Resource.uploaded_at.desc()).all()
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        'resources.html',
        resources=resources,
        categories=categories,
        q=q, cat=cat
    )


# 2. TÉLÉCHARGEMENT
@bp.route('/download/<int:res_id>')
@login_required
def download(res_id):
    res = Resource.query.get_or_404(res_id)
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        res.filename,
        as_attachment=True
    )


# 3. UPLOAD / PROPOSITION
@bp.route('/new', methods=['GET', 'POST'])
@login_required
def upload_resource():
    is_admin = (current_user.role == 'admin')
    form = ResourceForm()
    form.category.choices = [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]

    if form.validate_on_submit():
        f = form.file.data
        orig = secure_filename(f.filename)
        unique_name = f"{uuid.uuid4().hex}_{orig}"

        # 3.1. Sauvegarde physique
        folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(folder, exist_ok=True)
        f.save(os.path.join(folder, unique_name))

        # 3.2. Création en base
        res = Resource(
            title        = form.title.data,
            description  = form.description.data,
            filename     = unique_name,
            file_type    = f.mimetype,
            category_id  = form.category.data,
            uploaded_by  = current_user.id if is_admin else None,
            submitted_by = None   if is_admin else current_user.id,
            is_validated = is_admin
        )
        db.session.add(res)
        db.session.commit()

        flash(
          "Ressource ajoutée avec succès." if is_admin
          else "Proposition enregistrée, en attente de validation.",
          "success"
        )
        return redirect(url_for('resources.list_resources'))

    return render_template(
        'resource_form.html',
        form=form,
        is_admin=is_admin
    )


# 4. MODIFICATION (admin only)
@bp.route('/edit/<int:res_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_resource(res_id):
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

        # si on ré‐upload un fichier
        if form.file.data:
            old = os.path.join(current_app.config['UPLOAD_FOLDER'], res.filename)
            if os.path.exists(old):
                os.remove(old)

            newf = form.file.data
            name = f"{uuid.uuid4().hex}_{secure_filename(newf.filename)}"
            newf.save(os.path.join(current_app.config['UPLOAD_FOLDER'], name))
            res.filename  = name
            res.file_type = newf.mimetype

        db.session.commit()
        flash("Ressource mise à jour.", "success")
        return redirect(url_for('resources.list_resources'))

    return render_template(
        'resource_form.html',
        form=form,
        edit=True,
        resource=res
    )


# 5. SUPPRESSION (admin only)
@bp.route('/delete/<int:res_id>', methods=['POST'])
@login_required
@admin_required
def delete_resource(res_id):
    res = Resource.query.get_or_404(res_id)
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], res.filename)
    if os.path.exists(path):
        os.remove(path)
    db.session.delete(res)
    db.session.commit()
    flash("Ressource supprimée avec succès.", "success")
    return redirect(url_for('resources.list_resources'))
