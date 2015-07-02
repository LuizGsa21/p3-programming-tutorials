from flask import url_for
from marshmallow import fields

from app.helpers.utils import format_datetime
from app.api.schemas import UserSchema


class UserSettingSchema(UserSchema):
    date_joined = fields.Method('format_date')
    avatar = fields.Method('avatar_url')

    def avatar_url(self, obj):

        return url_for('static', filename='uploads/avatar/' + str(obj.avatar))

    def format_date(self, obj):
        return format_datetime(obj.date_joined)

    class Meta:
        fields = ('username', 'email', 'first_name', 'avatar', 'last_name', 'date_joined')

user_info_serializer = UserSettingSchema()