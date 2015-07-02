from marshmallow import Schema, fields
from flask import url_for
from app.helpers.utils import format_datetime


# shallow schemas
class CommentSchema(Schema):
    class Meta:
        fields = ('id', 'parent_id', 'user_id', 'message', 'subject', 'date_created', 'last_modified', 'article_id')


class UserSchema(Schema):
    avatar = fields.Method('avatar_path')

    def avatar_path(self, obj):
        return url_for('static', filename='uploads/avatar/' + obj.avatar)

    class Meta:
        fields = ('id', 'username', 'date_joined', 'avatar')


class CategorySchema(Schema):
    class Meta:
        fields = ('id', 'name')


class ArticleSchema(Schema):
    category = fields.Nested(CategorySchema)
    date_created = fields.Method('format_date')

    def format_date(self, obj):
        return str(obj.date_created)

    class Meta:
        fields = ('id', 'title', 'body', 'date_created', 'last_modified', 'category', 'author_id')


# nested schemas
class ArticleNestedSchema(ArticleSchema):
    author = fields.Nested(UserSchema)
    comments = fields.Nested(CommentSchema, many=True)

    class Meta:
        fields = ('id', 'title', 'body', 'date_created', 'category', 'author', 'comments', 'last_modified')


class CommentNestedSchema(CommentSchema):
    user = fields.Nested(UserSchema, only=('username', 'id', 'avatar'))

    class Meta:
        fields = ('id', 'parent_id', 'user', 'message', 'subject', 'date_created', 'last_modified', 'article_id')


# shallow schemas
user_serializer = UserSchema()

article_serializer = ArticleSchema()
articles_serializer = ArticleSchema(many=True)

comment_serializer = CommentSchema()
comments_serializer = CommentSchema(many=True)

# deep `nested` schemas
article_nested_serializer = ArticleNestedSchema()
articles_nested_serializer = ArticleNestedSchema(many=True)

comment_nested_serializer = CommentNestedSchema()
comments_nested_serializer = CommentNestedSchema(many=True)

