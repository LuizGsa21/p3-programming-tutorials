from marshmallow import fields
from ..model import UserSchema, CommentSchema


class CommentWithUserSchema(CommentSchema):
    user = fields.Nested(UserSchema, only=('username', 'id', 'avatar'))
    dateCreated = fields.DateTime()
    lastModified = fields.DateTime()

    class Meta:
        fields = ('id', 'parentId', 'user', 'message', 'subject', 'dateCreated', 'lastModified', 'articleId')