from marshmallow import fields, Schema
from ..general import (
    LoginManagerSchema, UserInfoSchema, NavbarSchema, ArticleWithAuthorSchema
)


class CategoryArticlesView(Schema):
    category = fields.String()
    user = fields.Nested(UserInfoSchema)
    loginManager = fields.Nested(LoginManagerSchema)
    navbar = fields.Nested(NavbarSchema)
    articles = fields.Nested(ArticleWithAuthorSchema, many=True)

    class Meta:
        ordered = True