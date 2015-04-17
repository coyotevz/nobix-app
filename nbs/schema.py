# -*- coding: utf-8 -*-

from marshmallow import Schema, fields
from nbs.models import Supplier


class _RefEntitySchema(Schema):
    id = fields.Integer()
    entity = fields.Nested('EntitySchema')

class AddressSchema(_RefEntitySchema):
    type = fields.String(attribute='address_type')
    city = fields.String()
    province = fields.String()
    postal_code = fields.String()


class PhoneSchema(_RefEntitySchema):
    type = fields.String(attribute='phone_type')
    prefix = fields.String()
    number = fields.String()
    extension = fields.String()


class EmailSchema(_RefEntitySchema):
    type = fields.String(attribute='email_type')
    email = fields.Email()


class ExtraFieldSchema(_RefEntitySchema):
    name = fields.String(attribute='field_name')
    value = fields.String(attribute='field_value')


class EntitySchema(Schema):
    id = fields.Integer()
    created = fields.DateTime()
    modified = fields.DateTime()
    address = fields.Nested(AddressSchema, many=True, exclude=('entity',))
    phone = fields.Nested(PhoneSchema, many=True, exclude=('entity',))
    email = fields.Nested(EmailSchema, many=True, exclude=('entity',))
    extra = fields.Nested(ExtraFieldSchema, many=True, attribute='extrafield',
                          exclude=('entity',))


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
    id = fields.Integer()
    fiscal_type = fields.String(attribute='fiscal_type_str')
    cuit = fields.String()


class SupplierSchema(EntitySchema):
    name = fields.String()
    fiscal_data = fields.Nested(FiscalDataSchema)
    customer_no = fields.String(default=None)
    payment_term = fields.Integer(default=None)
    leap_time = fields.Integer(default=None)
    freight_type = fields.String(attribute='freight_type_str')

    contacts = fields.Nested(SupplierContactSchema,
                             attribute='supplier_contacts',
                             many=True, exclude=('supplier',))

    bank_accounts = fields.Nested('BankAccountSchema', many=True,
                                  only=('id', 'bank', 'type'))

    def make_object(self, data):
        if 'freight_type_str' in data:
            data['freight_type'] = data.pop('freight_type_str')
        return Supplier(**data)


class PurchaseDocumentSchema(Schema):
    id = fields.Integer()
    type = fields.String(attribute='type_str')
    number = fields.String(attribute='number_display')
    issue_date = fields.Date()
    expiration_date = fields.Date()
    status = fields.String(attribute='status_str')
    supplier_id = fields.Integer()
    suplpier_name = fields.String(attribute='supplier.name')


class BankAccountSchema(Schema):
    id = fields.Integer()
    bank = fields.String(attribute='bank.name')
    bank_id = fields.Integer()
    branch = fields.String(attribute='bank_branch')
    type = fields.String(attribute='account_type_str')
    number = fields.String(attribute='account_number')
    cbu = fields.String(attribute='account_cbu')
    owner = fields.String(attribute='account_owner')
    supplier_id = fields.Integer()
    supplier_name = fields.String(attribute='supplier.name')


class BankSchema(Schema):
    id = fields.Integer()
    name = fields.String()
