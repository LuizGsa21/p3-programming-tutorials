from marshmallow import fields
from flask import url_for
from ..model import CategorySchema


class CategoryInfoSchema(CategorySchema):
    url = fields.Function(lambda category: url_for('frontend.category_articles', category=category.name))

    class Meta:
        fields = ('id', 'name', 'url')