# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from webargs import Arg, ValidationError
from webargs.flaskparser import use_args
from nbs.models import Supplier
from nbs.schema import SupplierSchema, BankAccountSchema

supplier_api = Blueprint('api.supplier', __name__, url_prefix='/api/suppliers')
supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)
bank_acc_schema = BankAccountSchema(many=True, exclude=('supplier_id', 'supplier_name'))

@supplier_api.route('', methods=['GET'])
def list():
    """
    Returns a paginated list of suppliers that match with the given
    conditions.
    """

    return jsonify(objects=suppliers_schema.dump(Supplier.query).data)


@supplier_api.route('', methods=['POST'])
def add():
    return jsonify({'action': 'POST'})


@supplier_api.route('/<int:id>', methods=['GET'])
def get(id):
    """Returns an individual supplier given an id"""
    supplier = Supplier.query.get_or_404(id)
    result = supplier_schema.dump(supplier)
    return jsonify(result.data)

@supplier_api.route('/<rangelist:ids>', methods=['GET'])
def get_many(ids):
    suppliers = []
    for id in ids:
        s = Supplier.query.get(id)
        if s is not None:
            suppliers.append(s)
    result = suppliers_schema.dump(suppliers)
    return jsonify(objects=result.data)


update_args = {
    'leap_time': Arg(int, allow_missing=True),
    'payment_term': Arg(int, allow_missing=True),
}

@supplier_api.route('/<int:id>', methods=['PUT', 'PUSH'])
@use_args(update_args)
def update(args, id):
    args['action'] = 'PUT {0}'.format(id)
    return jsonify(args)


@supplier_api.route('/<int:id>', methods=['DELETE'])
def delete(id):
    return jsonify({'action': 'DELETE {0}'.format(id)})

# This is a shortcut, to work with bank accounts use corresponding api
@supplier_api.route('/<int:id>/accounts', methods=['GET'])
def get_supplier_accounts(id):
    supplier = Supplier.query.get(id)

    return jsonify(objects=bank_acc_schema.dump(supplier.bank_accounts).data)
