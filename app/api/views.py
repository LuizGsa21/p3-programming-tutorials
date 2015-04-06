from flask import Blueprint, jsonify
from schemas import ArticleSchema, CategorySchema
from app.models import Article, Comment, User, Category

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/articles/')
def articles_to_json():
    articles = Article.query.all()
    serializer = ArticleSchema(many=True)
    result, error = serializer.dump(articles)
    return jsonify(articles=result)


@api.route('/categories/')
def categories_to_json():
    categories = Category.query.all()
    serializer = CategorySchema(many=True)
    result, error = serializer.dump(categories)
    return jsonify(categories=result)