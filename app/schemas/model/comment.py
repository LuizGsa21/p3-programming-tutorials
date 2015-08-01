from marshmallow import Schema


class CommentSchema(Schema):

    class Meta:
        fields = ('id', 'parentId', 'userId', 'message', 'subject', 'dateCreated', 'lastModified', 'articleId')