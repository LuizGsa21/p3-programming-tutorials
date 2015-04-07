from flask import Blueprint, jsonify
from schemas import ArticleSchema, CategorySchema, article_serializer, articles_serializer
from app.models import Article, Comment, User, Category

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/articles/')
@api.route('/articles/all/')
def articles_to_json():
    articles = Article.query.all()
    if articles is None:
        result = None
    else:
        result, error = articles_serializer.dump(articles)
    return jsonify(articles=result)


@api.route('/articles/<int:id>/')
def article_to_json(id):
    article = Article.query.get(id)
    if article is None:
        result = None
    else:
        result, error = article_serializer.dump(article)
    return jsonify(article=result)


@api.route('/categories/')
def categories_to_json():
    categories = Category.query.all()
    serializer = CategorySchema(many=True)
    result, error = serializer.dump(categories)
    return jsonify(categories=result)