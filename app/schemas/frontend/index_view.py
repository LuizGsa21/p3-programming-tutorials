"""
    Unique Schemas for `frontend.article` view
"""
from marshmallow import fields, Schema
from ..general import (
    LoginManagerSchema, UserInfoSchema, NavbarSchema
)


class IndexViewSchema(Schema):
    user = fields.Nested(UserInfoSchema)
    loginManager = fields.Nested(LoginManagerSchema)
    navbar = fields.Nested(NavbarSchema)

    class Meta:
        ordered = True
