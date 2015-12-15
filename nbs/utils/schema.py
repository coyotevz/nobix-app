# -*- coding: utf-8 -*-

from marshmallow import Schema, fields
from nbs.models import Employee


class _RefEntitySchema(Schema):
    id = fields.Integer()
    entity = fields.Nested('EntitySchema')

class TimestampSchema(Schema):
    created = fields.DateTime(dump_only=True)
    modified = fields.DateTime(dump_only=True)


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


class EntitySchema(TimestampSchema):
    id = fields.Integer(dump_only=True)
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
    cuit = fields.Method('serialize_cuit', 'deserialize_cuit')


    def serialize_cuit(self, obj):
        c = obj.cuit
        return "{}-{}-{}".format(c[:2], c[2:10], c[10:])

    def deserialize_cuit(self, val):
        return val.replace("-", "")


class PurchaseDocumentSchema(TimestampSchema):
    id = fields.Integer()
    type = fields.String(attribute='type_str')
    number = fields.String(attribute='number_display')
    amount = fields.Decimal(places=2, as_string=True)
    issue = fields.Date(attribute='issue_date')
    expiration = fields.Date(attribute='expiration_date')
    status = fields.String(attribute='status_str')
    supplier_id = fields.Integer()
    supplier_name = fields.String(attribute='supplier.name')


class ProductSchema(TimestampSchema):
    id = fields.Integer()
    sku = fields.String()
    description = fields.String()
    notes = fields.String()
    price = fields.Decimal(places=2, as_string=True)


#class BankAccountSchema(Schema):
#    id = fields.Integer()
#    bank = fields.String(attribute='bank.name')
#    bank_id = fields.Integer()
#    branch = fields.String(attribute='bank_branch')
#    type = fields.String(attribute='account_type_str')
#    number = fields.String(attribute='account_number')
#    cbu = fields.String(attribute='account_cbu')
#    owner = fields.String(attribute='account_owner')
#    supplier_id = fields.Integer()
#    supplier_name = fields.String(attribute='supplier.name')


class BankSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class EmployeeSchema(EntitySchema):
    first_name = fields.String()
    last_name = fields.String()
    birth_date = fields.Date()
    hire_date = fields.Date()
    cuil = fields.Method('serialize_cuil', 'deserialize_cuil')
    file_no = fields.Integer()
    user_code = fields.Integer()

    def serialize_cuil(self, obj):
        c = obj.cuil
        return "{}-{}-{}".format(c[:2], c[2:10], c[10:])

    def deserialize_cuil(self, val):
        return val.replace("-", "")

    def make_object(self, data):
        return Employee(**data)


class IntervalInfoSchema(Schema):
    input = fields.Time()
    output = fields.Time()
    late = fields.TimeDelta()


class AttendanceRecordSchema(Schema):
    day = fields.Date()
    intervals = fields.Nested(IntervalInfoSchema, many=True)
