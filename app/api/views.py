from flask import Blueprint, jsonify
from schemas import ArticleSchema
from app.models import Article, Comment, User

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/articles/')
def articles_to_json():
    articles = Article.query.all()
    serializer = ArticleSchema(many=True)
    result, error = serializer.dump(articles)
    return jsonify(articles=result)