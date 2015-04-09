from flask import Blueprint, jsonify
from schemas import ArticleSchema, CategorySchema, article_serializer, articles_serializer
from app.models import Article, Comment, User, Category

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/articles/')
@api_bp.route('/articles/all/')
def articles_to_json():
    articles = Article.query.all()
    if articles is None:
        result = None
    else:
        result, error = articles_serializer.dump(articles)
    return jsonify(articles=result)


@api_bp.route('/articles/<int:id>/')
def article_to_json(id):
    article = Article.query.get(id)
    if article is None:
        result = None
    else:
        result, error = article_serializer.dump(article)
    return jsonify(article=result)


@api_bp.route('/categories/')
def categories_to_json():
    categories = Category.query.all()
    serializer = CategorySchema(many=True)
    result, error = serializer.dump(categories)
    return jsonify(categories=result)