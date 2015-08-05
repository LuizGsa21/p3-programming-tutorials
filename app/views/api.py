from flask import Blueprint, jsonify, flash, request
from flask_login import current_user
from app.models import Article, Category, User
from app.schemas import (
    article_serializer, category_serializer,
    user_info_serializer, user_serializer
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/articles/')
@api_bp.route('/articles/all/')
def get_articles():
    articles = Article.query.all()
    if articles:
        articles = article_serializer.dump(articles, many=True).data
    result = {
        'articles': articles
    }
    return jsonify(result=result)


@api_bp.route('/articles/<int:id>/')
def get_article_by_id(id):
    article = Article.query.get(id)
    if article:
        article = article_serializer.dump(article).data
    result = {
        'article': article
    }
    return jsonify(result=result)

@api_bp.route('/articles/author/<int:id>/')
def get_articles_by_author_id(id):
    articles = Article.query.filter_by(authorId=id)
    if articles:
        articles = article_serializer.dump(articles, many=True).data
    result = {
        'articles': articles
    }
    return jsonify(result=result)


@api_bp.route('/categories/')
def get_categories():
    categories = Category.query.all()
    if categories:
        categories = category_serializer.dump(categories).data
    result = {
        'categories': categories
    }
    return jsonify(result=result)