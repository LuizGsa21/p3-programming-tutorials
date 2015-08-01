from marshmallow import fields
from ..model import UserSchema, ArticleSchema


class ArticleWithAuthorSchema(ArticleSchema):
    author = fields.Nested(UserSchema)

    class Meta:
        fields = ('id', 'title', 'body', 'dateCreated', 'category', 'lastModified', 'author', 'url')