# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class SupplierSchema(Schema):

    id = fields.Integer()
    name = fields.String()
    fancy_name = fields.String()
    full_name = fields.String()
    payment_term = fields.Integer()
    leap_time = fields.Integer()
    freight_type = fields.String(attribute='freight_type_str')
    created = fields.DateTime()
    modified = fields.DateTime()
