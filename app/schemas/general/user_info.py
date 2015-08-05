from flask import url_for
from marshmallow import fields
from flask_login import current_user as c_user
from ..model import UserSchema


class UserInfoSchema(UserSchema):
    isLoggedIn = fields.Function(lambda obj: obj.id == c_user.id and c_user.is_authenticated())
    isAdmin = fields.Function(lambda obj: obj.isAdmin)
    avatar = fields.Function(lambda obj: url_for('static', filename='uploads/avatar/' + obj.avatar))
    dateJoined = fields.DateTime()

    class Meta:
        fields = ('id', 'username', 'email', 'firstName', 'avatar', 'lastName', 'dateJoined', 'isAdmin', 'isLoggedIn')