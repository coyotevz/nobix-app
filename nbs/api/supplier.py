# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, url_for, abort
from webargs.flaskparser import parser
from marshmallow import Schema, fields, post_load, validates, ValidationError
from marshmallow.validate import Length

from nbs.models import db, Supplier, BankAccount, Bank
from nbs.utils.api import build_result
from nbs.utils.schema import EntitySchema, FiscalDataSchema
from nbs.utils.validators import validate_cbu as is_valid_cbu


class SupplierSchema(EntitySchema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=[Length(min=2)])
    fiscal_data = fields.Nested(FiscalDataSchema)
    customer_no = fields.String()
    payment_term = fields.Integer()
    leap_time = fields.Integer()
    freight_type = fields.String(attribute='freight_type_str')

    bank_accounts = fields.Nested('BankAccountSchema', many=True,
                                  only=('id', 'bank', 'type'))

    @validates('name')
    def validate_unique_name(self, value):
        exists = Supplier.query.filter(Supplier.name==value).first()
        if exists is not None:
            if self.context.get('supplier_id', None) == exists.id:
                return True
            raise ValidationError('Supplier name must be unique',
                                  status_code=409)

    @validates('freight_type')
    def validate_freight_type(self, value):
        if value not in Supplier._freight_types.keys():
            raise ValidationError('Invalid freight_type, consult {}'.format(
                url_for('.get_freight_types', _external=True)))

    @post_load
    def make_supplier(self, data):
        if 'freight_type_str' in data:
            data['freight_type'] = data.pop('freight_type_str')
        if self.partial:
            return data
        return Supplier(**data)

    class Meta:
        strict = True


class BankAccountSchema(Schema):
    id = fields.Integer(dump_only=True)
    bank = fields.String(attribute='bank.name')
    bank_id = fields.Integer(required=True)
    branch = fields.String(attribute='bank_branch', required=True)
    type = fields.String(attribute='account_type_str')
    number = fields.String(attribute='account_number', required=True)
    cbu = fields.String(attribute='account_cbu', validate=is_valid_cbu)
    owner = fields.String(attribute='account_owner')
    supplier_id = fields.Integer(required=True)
    supplier_name = fields.String(attribute='supplier.name')

    @validates('bank_id')
    def validate_bank_id(self, value):
        bank = Bank.query.get(int(value))
        if not bank:
            raise ValidationError('Invalid bank_id, consult {}'.format(
                url_for('api.bank.list_banks', _external=True)))

    @validates('type')
    def validate_type(self, value):
        if value not in BankAccount._account_types.keys():
            raise ValidationError('Invalid type, consult {}'.format(
                url_for('api.bank.list_account_types', _external=True)))

    @post_load
    def make_bank_account(self, data):
        if 'account_type_str' in data:
            data['account_type'] = data.pop('account_type_str')
        if 'account_cbu' in data:
            data['account_cbu'] = data.pop('account_cbu').replace(" ", "")
        if self.partial:
            return data
        return BankAccount(**data)

    class Meta:
        strict = True


supplier_api = Blueprint('api.supplier', __name__, url_prefix='/api/suppliers')

supplier_schema = SupplierSchema()


@supplier_api.route('')
def list_suppliers():
    """
    Returns a paginated list of suppliers that match with the given conditions.
    """
    q = Supplier.query.order_by(Supplier.name)
    return build_result(q, SupplierSchema(exclude=('bank_accounts',)))

@supplier_api.route('/<int:id>')
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    return build_result(supplier, supplier_schema)

@supplier_api.route('/<rangelist:ids>')
def list_suppliers_range(ids):
    suppliers = []
    for id in ids:
        s = Supplier.query.get(id)
        if s is not None:
            suppliers.append(s)
    return build_result(suppliers, supplier_schema)

@supplier_api.route('', methods=['POST'])
def new_supplier():
    supplier = parser.parse(supplier_schema)
    db.session.add(supplier)
    db.session.commit()
    return '', 201, {'Location': url_for('.get_supplier', id=supplier.id,
                                         _external=True)}

@supplier_api.route('/<int:id>', methods=['PATCH'])
def update_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    schema = SupplierSchema(partial=True, context={'supplier_id': id})
    args = parser.parse(schema)
    for k, v in args.items():
        setattr(supplier, k, v)
    db.session.commit()
    return '', 204

@supplier_api.route('/<int:id>', methods=['DELETE'])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    return '', 204

@supplier_api.route('/freight_types')
def list_freight_types():
    return jsonify(**Supplier._freight_types)

@supplier_api.route('/<int:id>/accounts')
def list_bank_accounts(id):
    supplier = Supplier.query.get_or_404(id)
    q = BankAccount.query.filter(BankAccount.supplier==supplier)
    return build_result(q, BankAccountSchema(exclude=('supplier_name')))

@supplier_api.route('/<int:id>/accounts', methods=['POST'])
def new_bank_account(id):
    supplier = Supplier.query.get_or_404(id)
    account = parser.parse(BankAccountSchema(exclude=('supplier_id',)))
    account.supplier = supplier
    db.session.add(account)
    db.session.commit()
    return '', 201, {'Location': url_for('.get_bank_account', id=supplier.id,
                                         baid=account.id, _external=True)}

def get_bank_account_for_supplier_or_404(supplier_id, bank_account_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    bank_account = BankAccount.query.get_or_404(bank_account_id)
    if bank_account.supplier != supplier:
        abort(404)
    return bank_account

@supplier_api.route('/<int:id>/accounts/<int:baid>')
def get_bank_account(id, baid):
    account = get_bank_account_for_supplier_or_404(id, baid)
    return build_result(account, BankAccountSchema())

@supplier_api.route('/<int:id>/accounts/<int:baid>', methods=['PATCH'])
def update_bank_account(id, baid):
    account = get_bank_account_for_supplier_or_404(id, baid)
    args = parser.parse(BankAccountSchema(partial=True))
    for k, v in args.items():
        setattr(account, k, v)
    db.session.commit()
    return '', 204

@supplier_api.route('/<int:id>/accounts/<int:baid>', methods=['DELETE'])
def delete_bank_account(id, baid):
    account = get_bank_account_for_supplier_or_404(id, baid)
    db.session.delete(account)
    db.session.commit()
    return '', 204
