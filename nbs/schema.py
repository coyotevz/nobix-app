# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class SupplierSchema(Schema):

    id = fields.Integer()
    name = fields.String()
    payment = fields.Integer()
    full_desc = fields.String()
