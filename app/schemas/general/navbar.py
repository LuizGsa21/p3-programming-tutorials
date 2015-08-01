from marshmallow import Schema, fields, post_dump
from flask import url_for
from .category_info import CategoryInfoSchema


class NavbarSchema(Schema):
    home = fields.Function(lambda _: url_for('frontend.index'))
    categories = fields.Nested(CategoryInfoSchema, many=True)
    register = fields.Function(lambda _: url_for('frontend.register'))
    login = fields.Function(lambda _: url_for('frontend.login'))
    profile = fields.Function(lambda _: url_for('user.profile'))
    logout = fields.Function(lambda _: url_for('frontend.logout'))

    class Meta:
        ordered = True

    @post_dump(raw=False)
    def order_urls(self, data):
        # wrap the urls in a list to guarantee order on client side
        urls = []
        for name, url in data.items():
            urls.append({
                'name': name.capitalize(),
                'url': url
            })
        return urls