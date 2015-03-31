# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class AddressSchema(Schema):

    id = fields.Integer()
    type = fields.String(attribute='address_type')
    city = fields.String()
    province = fields.String()
    postal_code = fields.String()


class PhoneSchema(Schema):

    id = fields.Integer()
    type = fields.String(attribute='phone_type')
    prefix = fields.String()
    number = fields.String()
    extension = fields.String()


class EmailSchema(Schema):

    id = fields.Integer()
    type = fields.String(attribute='email_type')
    email = fields.Email()


class EntitySchema(Schema):

    id = fields.Integer()
    created = fields.DateTime()
    modified = fields.DateTime()
    address = fields.Nested(AddressSchema, many=True)
    phone = fields.Nested(PhoneSchema, many=True)
    email = fields.Nested(EmailSchema, many=True)
    extra = fields.Nested(ExtraFieldSchema, many=True, attribute='extrafield')


class ContactSchema(EntitySchema):

    first_name = fields.String()
    last_name = fields.String()


class SupplierContactSchema(Schema):

    id = fields.Integer(attribute='contact.id')
    first_name = fields.String(attribute='contact.first_name')
    last_name = fields.String(attribute='contact.last_name')
    supplier = fields.Nested('SupplierSchema', exclude=('contacts',))
    role = fields.String()


class FiscalDataSchema(Schema):

    fiscal_type = fields.String(attribute='fiscal_type_str')
    cuit = fields.String()


class SupplierSchema(EntitySchema, FiscalDataSchema):

    name = fields.String()
    fancy_name = fields.String()
    full_name = fields.String()
    payment_term = fields.Integer(default=None)
    leap_time = fields.Integer(default=None)
    freight_type = fields.String(attribute='freight_type_str')

    contacts = fields.Nested(SupplierContactSchema, attribute='supplier_contacts',
                             many=True, exclude=('supplier',))
    bank_accounts = fields.Nested('BankAccountSchema', many=True,
                                  only=('id', 'bank', 'type'))


class BankAccountSchema(Schema):

    id = fields.Integer()
    bank = fields.String(attribute='bank.name')
    branch = fields.String(attribute='bank_branch')
    type = fields.String(attribute='account_type_str')
    number = fields.String(attribute='account_number')
    cbu = fields.String(attribute='account_cbu')
    owner = fields.String(attribute='account_owner')
    supplier_id = fields.String(attribute='supplier.id')
    suplpier_name = fields.String(attribute='supplier.name')
