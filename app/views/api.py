from flask import Blueprint, jsonify, flash, request
from flask_login import current_user
from app.models import Article, Category, User
from app.schemas import (
    article_serializer, category_serializer,
    user_info_serializer, user_serializer
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/articles/', methods=['GET'])
@api_bp.route('/articles/all', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    if articles:
        articles = article_serializer.dump(articles, many=True).data
    result = {
        'articles': articles
    }
    return jsonify(result=result)


@api_bp.route('/articles/<int:id>', methods=['GET'])
def get_article_by_id(id):
    article = Article.query.get(id)
    if article:
        article = article_serializer.dump(article).data
    result = {
        'article': article
    }
    return jsonify(result=result)

@api_bp.route('/articles/author/<int:id>', methods=['GET'])
def get_articles_by_author_id(id):
    articles = Article.query.filter_by(authorId=id)
    if articles:
        articles = article_serializer.dump(articles, many=True).data
    result = {
        'articles': articles
    }
    return jsonify(result=result)


@api_bp.route('/categories/', methods=['GET'])
@api_bp.route('/categories/all', methods=['GET'])
def get_categories():
    categories = Category.query.order_by(Category.name).all()
    if categories:
        categories = category_serializer.dump(categories).data
    result = {
        'categories': categories
    }
    return jsonify(result=result)

@api_bp.route('/categories/<int:id>', methods=['GET'])
def get_category_by_id(id):
    category = Category.query.get(id)
    if category:
        category = category_serializer.dump(category).data
    result = {
        'category': category
    }
    return jsonify(result=result)


@api_bp.route('/users/', methods=['GET'])
@api_bp.route('/users/all', methods=['GET'])
def get_users():
    users = User.query.order_by(User.id).all()
    if users:
        if current_user.is_admin():
            # user_info_serializer contains user emails
            users = user_info_serializer.dump(users, many=True).data
        else:
            users = user_serializer.dump(users, many=True).data
    result = {
        'users': users
    }
    return jsonify(result=result)

@api_bp.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    if user:
        if current_user.id == id or current_user.is_admin():
            # user_info_serializer contains user emails
            user = user_info_serializer.dump(user).data
        else:
            user = user_serializer.dump(user).data
    result = {
        'user': user
    }
    return jsonify(result=result)