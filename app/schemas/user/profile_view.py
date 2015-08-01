"""
    Unique Schemas for `frontend.article` view
"""
from marshmallow import fields, Schema
from ..general import (
    LoginManagerSchema, UserInfoSchema, NavbarSchema
)

from ..model import ArticleSchema


class ProfileViewSchema(Schema):
    user = fields.Nested(UserInfoSchema)
    articles = fields.Nested(ArticleSchema, many=True)
    loginManager = fields.Nested(LoginManagerSchema)
    navbar = fields.Nested(NavbarSchema)

    class Meta:
        ordered = True
