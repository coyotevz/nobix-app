# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class EntitySchema(Schema):

    id = fields.Integer()


class ContactSchema(EntitySchema):

    first_name = fields.String()
    last_name = fields.String()


class SupplierContactSchema(Schema):

    id = fields.Integer(attribute='contact.id')
    first_name = fields.String(attribute='contact.first_name')
    last_name = fields.String(attribute='contact.last_name')
    supplier = fields.Nested('SupplierSchema', exclude=('contacts',))
    role = fields.String()


class SupplierSchema(Schema):

    id = fields.Integer()
    name = fields.String()
    fancy_name = fields.String()
    full_name = fields.String()
    payment_term = fields.Integer(default=None)
    leap_time = fields.Integer(default=None)
    freight_type = fields.String(attribute='freight_type_str')
    created = fields.DateTime()
    modified = fields.DateTime()

    contacts = fields.Nested(SupplierContactSchema, attribute='supplier_contacts',
                             many=True, exclude=('supplier',))
