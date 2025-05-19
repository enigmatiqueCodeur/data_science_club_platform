from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
from models.resource import Resource
from models.faq import Faq
from app import db
from sqlalchemy import func

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/search_resources', methods=['POST'])
@login_required
def search_resources():
    q = request.json.get('query', '').strip()
    if not q:
        return jsonify([])

    # Full-text simple (PostgreSQL) :
    ts = func.to_tsvector('french', Resource.title + ' ' + Resource.description)
    results = Resource.query \
        .filter(ts.match(q)) \
        .limit(10) \
        .all()
    return jsonify([{'id': r.id, 'title': r.title} for r in results])

@bp.route('/faq', methods=['POST'])
@login_required
def faq():
    q = request.json.get('question', '').lower()
    faq = Faq.query.filter(Faq.question.ilike(f"%{q}%")).first()
    if faq:
        return jsonify({'answer': faq.answer})
    return jsonify({'answer': "Désolé, je n'ai pas la réponse. Essaie une autre question !"})
