# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, abort
from sqlalchemy.exc import IntegrityError
from webargs.flaskparser import parser
from marshmallow import Schema, fields, validates, ValidationError, post_load
from marshmallow.validate import Length

from nbs.models import db, Bank, BankAccount, BankAccountType
from nbs.utils.api import build_result
from nbs.utils.validators import validate_cuit


class BankSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[Length(min=2)])
    bcra_code = fields.String(validate=[Length(max=8)])
    cuit = fields.String()

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
            if self.context.get('bank_account_type_id', None) == exists.id:
                return True
            raise ValidationError('BankAccountType name must be unique.',
                                  status_code=409)

    @validates('abbr')
    def validate_unique_abbr(self, value):
        exists = BankAccountType.query.filter(BankAccountType.abbr==value).first()
        if exists is not None:
            if self.context.get('bank_account_type_id', None) == exists.id:
                return True
            raise ValidationError('BankAccountType abbr must be unique.',
                                  status_code=409)
    @post_load
    def make_acc_type(self, data):
        if self.partial:
            return data
        return BankAccountType(**data)


bank_api = Blueprint('api.bank', __name__, url_prefix='/api/banks')

@bank_api.route('')
def list_banks():
    q = Bank.query.order_by(Bank.name)
    return build_result(q, BankSchema())

@bank_api.route('', methods=['POST'])
def new_bank():
    bank = parser.parse(BankSchema(strict=True))
    db.session.add(bank)
    db.session.commit()
    # only return id of created Bank, we don't have individual receivers
    return jsonify({'id': bank.id}), 201

@bank_api.route('/<int:id>', methods=['PATCH'])
def update_bank(id):
    args = parser.parse(BankSchema(partial=True))
    bank = Bank.query.get_or_404(id)
    bank.name = args['name']
    db.session.commit()
    return '', 204

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
    return jsonify({'id': acc_type.id}), 201
