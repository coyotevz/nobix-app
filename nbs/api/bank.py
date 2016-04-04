# -*- coding: utf-8 -*-

from flask import Blueprint, abort, url_for
from sqlalchemy.exc import IntegrityError
from webargs.flaskparser import parser
from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow.validate import Length

from nbs.models import db, Bank, BankAccount, BankAccountType
from nbs.lib.rest import build_result
from nbs.utils.validators import validate_cuit


class BankSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[Length(min=2)])
    bcra_code = fields.String(validate=[Length(max=8)])
    cuit = fields.String(validate=[Length(equal=11)])

    @validates('name')
    def validate_unique_name(self, value):
        exists = Bank.query.filter(Bank.name==value).first()
        if exists is not None:
            if self.context.get('bank_id', None) == exists.id:
                return True
            raise ValidationError('Bank name must be unique.', status_code=409)

    @validates('cuit')
    def validate_valid_cuit(self, value):
        if not validate_cuit(value):
            raise ValidationError("CUIT field invalid.")
        return True

    @post_load
    def make_bank(self, data):
        if self.partial:
            return data
        return Bank(**data)


class BankAccountTypeSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[Length(min=2)])
    abbr = fields.String()

    @validates('name')
    def validate_unique_name(self, value):
        exists = BankAccountType.query.filter(BankAccountType.name==value).first()
        if exists is not None:
            if self.context.get('acc_type_id', None) == exists.id:
                return True
            raise ValidationError('BankAccountType name must be unique.',
                                  status_code=409)

    @validates('abbr')
    def validate_unique_abbr(self, value):
        exists = BankAccountType.query.filter(BankAccountType.abbr==value).first()
        if exists is not None:
            if self.context.get('acc_type_id', None) == exists.id:
                return True
            raise ValidationError('BankAccountType abbr must be unique.',
                                  status_code=409)
    @post_load
    def make_acc_type(self, data):
        if self.partial:
            return data
        return BankAccountType(**data)


bank_api = Blueprint('api.bank', __name__, url_prefix='/api/v1/banks')

@bank_api.route('')
def list_banks():
    q = Bank.query.order_by(Bank.name)
    return build_result(q, BankSchema())

@bank_api.route('', methods=['POST'])
def new_bank():
    bank = parser.parse(BankSchema(strict=True))
    db.session.add(bank)
    db.session.commit()
    return (build_result(bank, BankSchema()), 201,
            {'Location': url_for('.get_bank', id=bank.id)})

@bank_api.route('/<int:id>')
def get_bank(id):
    bank = Bank.query.get_or_404(id)
    return build_result(bank, BankSchema())

@bank_api.route('/<int:id>', methods=['PATCH'])
def update_bank(id):
    bank = Bank.query.get_or_404(id)
    args = parser.parse(BankSchema(strict=True, partial=True,
                                   context={'bank_id': bank.id}))
    for key, value in args.items():
        setattr(bank, key, value)
    db.session.commit()
    return build_result(bank, BankSchema())

@bank_api.route('/<int:id>', methods=['DELETE'])
def delete_bank(id):
    bank = Bank.query.get_or_404(id)
    db.session.delete(bank)
    try:
        db.session.commit()
    except IntegrityError:
        abort(409, description='Unable to delete bank')
    return '', 204

@bank_api.route('/account_types')
def list_account_types():
    q = BankAccountType.query.order_by(BankAccountType.name)
    return build_result(q, BankAccountTypeSchema())

@bank_api.route('/account_types', methods=['POST'])
def new_accout_type():
    acc_type = parser.parse(BankAccountTypeSchema(strict=True))
    db.session.add(acc_type)
    db.session.commit()
    return (build_result(acc_type, BankAccountTypeSchema()), 201,
            {'Location': url_for('.update_account_type', id=acc_type.id)})

@bank_api.route('/account_types/<int:id>', methods=['PATCH'])
def update_account_type(id):
    acc_type = BankAccountType.query.get_or_404(id)
    args = parser.parse(BankAccountTypeSchema(strict=True, partial=True,
                        context={'acc_type_id': acc_type.id}))
    for key, value in args.items():
        setattr(acc_type, key, value)
    db.session.commit()
    return build_result(acc_type, BankAccountTypeSchema())

@bank_api.route('/account_types/<int:id>', methods=['DELETE'])
def delete_account_type(id):
    acc_type = BankAccountType.query.get_or_404(id)
    db.session.delete(acc_type)
    try:
        db.session.commit()
    except IntegrityError:
        abort(409, description='Unable to delete account type')
    return '', 204
