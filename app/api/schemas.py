from marshmallow import Schema, fields
from app.utils import format_datetime


class CommentSchema(Schema):
    class Meta:
        fields = ('id', 'body', 'parent_comment_id', 'date_created', 'article_id')


class UserSchema(Schema):
    class Meta:
        fields = ('id', 'username', 'date_joined')


class CategorySchema(Schema):
    class Meta:
        fields = ('id', 'name')


class ArticleSchema(Schema):
    category = fields.Nested(CategorySchema)
    author = fields.Nested(UserSchema)
    comments = fields.Nested(CommentSchema, many=True)
    date_created = fields.Method('format_date')

    def format_date(self, obj):
        return format_datetime(obj.date_created, 'standard')

    class Meta:
        fields = ('id', 'title', 'body', 'date_created', 'category', 'author', 'comments')

article_serializer = ArticleSchema()
articles_serializer = ArticleSchema(many=True)
