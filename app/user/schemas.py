from marshmallow import Schema, fields
from app.utils import format_datetime
from app.api.schemas import UserSchema, articles_serializer, article_serializer


class UserSettingSchema(UserSchema):
    date_joined = fields.Method('format_date')

    def format_date(self, obj):
        return format_datetime(obj.date_joined)

    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name', 'date_joined')

user_info_serializer = UserSettingSchema()