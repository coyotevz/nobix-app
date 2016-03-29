# -*- coding: utf-8 -*-

from flask import request, url_for
from nbs.models import db, Product
from nbs.schema import ProductSchema
from nbs.utils.api import ResourceApi, build_result, route

p_schema = ProductSchema()


class ProductApi(ResourceApi):
    route_base = 'products'

    @classmethod
    def get_obj(cls, id):
        return Product.query.get_or_404(id)

    def index(self):
        return build_result(Product.query, p_schema)

    @route('<int:id>')
    def get(self, id):
        product = self.get_obj(id)
        return build_result(product, p_schema)
