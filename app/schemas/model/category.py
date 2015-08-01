from marshmallow import Schema


class CategorySchema(Schema):

    class Meta:
        fields = ('id', 'name')