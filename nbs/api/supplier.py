# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from nbs.models import Supplier
from nbs.schema import SupplierSchema

supplier_api = Blueprint('api.supplier', __name__, url_prefix='/api/suppliers')
supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)

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


@supplier_api.route('/<int:id>', methods=['PUT', 'PUSH'])
def update(id):
    return jsonify({'action': 'PUT {0}'.format(id)})


@supplier_api.route('/<int:id>', methods=['DELETE'])
def delete(id):
    return jsonify({'action': 'DELETE {0}'.format(id)})

@supplier_api.route('/<int:id>/accounts', methods=['GET'])
def get_supplier_accounts(id):
    supplier = Supplier.query.get(id)

    return jsonify(objects=[bank_acc_serializer.dump(acc).data for acc in
                            supplier.bank_accounts])
