from marshmallow import Schema, fields
from .category import CategorySchema


class ArticleSchema(Schema):
    category = fields.Nested(CategorySchema)
    dateCreated = fields.DateTime()
    lastModified = fields.DateTime()

    class Meta:
        fields = ('id', 'title', 'body', 'dateCreated', 'lastModified', 'category', 'authorId', 'url')