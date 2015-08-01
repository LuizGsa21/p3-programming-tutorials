"""
    Unique Schemas for `frontend.article` view
"""
from flask import url_for
from flask_login import current_user
from marshmallow import fields, Schema
from ..general import (
    LoginManagerSchema, UserInfoSchema, CommentWithUserSchema,
    ArticleWithAuthorSchema, NavbarSchema
)


class CommentListSchema(CommentWithUserSchema):
    action = fields.Method('get_action')
    userId = fields.String(attribute='user.id')
    username = fields.String(attribute='user.username')
    userAvatar = fields.Function(lambda obj: url_for('static', filename='uploads/avatar/' + obj.user.avatar))
    formName = fields.Method('get_form')

    def get_action(self, obj):
        if current_user.is_anonymous() or obj.userId != current_user.id:
            return 'Reply'
        else:
            return 'Edit'

    def get_form(self, obj):
        if current_user.is_anonymous() or obj.userId != current_user.id:
            return 'AddReplyForm'
        else:
            return 'EditCommentForm' if obj.parentId is None else 'EditReplyForm'

    class Meta:
        fields = (
            'id', 'parentId', 'message', 'subject', 'dateCreated', 'lastModified', 'articleId',
            'userId', 'username', 'userAvatar', 'action', 'formName'
        )


class ArticleViewSchema(Schema):
    user = fields.Nested(UserInfoSchema)
    article = fields.Nested(ArticleWithAuthorSchema)
    comments = fields.Nested(CommentListSchema, many=True)
    loginManager = fields.Nested(LoginManagerSchema)
    navbar = fields.Nested(NavbarSchema)

    class Meta:
        ordered = True
