from flask import url_for
from marshmallow import fields
from flask_login import current_user
from ..model import UserSchema


class UserInfoSchema(UserSchema):
    isLoggedIn = fields.Function(lambda obj: current_user.is_authenticated())
    avatar = fields.Function(lambda obj: url_for('static', filename='uploads/avatar/' + obj.avatar))
    dateJoined = fields.DateTime()

    class Meta:
        fields = ('username', 'email', 'firstName', 'avatar', 'lastName', 'dateJoined', 'isLoggedIn')