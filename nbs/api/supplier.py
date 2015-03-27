# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from nbs.models import Supplier

supplier_api = Blueprint('api.supplier', __name__, url_prefix='/api/suppliers')


@supplier_api.route('', methods=['GET'])
def list():
    """
    Returns a paginated list of suppliers that match with the given
    conditions.
    """
    return jsonify(Supplier.query.all())


@supplier_api.route('', methods=['POST'])
def add():
    return jsonify({'action': 'POST'})


@supplier_api.route('/<int:id>', methods=['GET'])
def get(id):
    """Returns an individual supplier given an id"""
    supplier = Supplier.query.get_or_404(id)
    return jsonify(supplier)


@supplier_api.route('/<int:id>', methods=['PUT', 'PUSH'])
def update(id):
    return jsonify({'action': 'PUT {0}'.format(id)})


@supplier_api.route('/<int:id>', methods=['DELETE'])
def delete(id):
    return jsonify({'action': 'DELETE {0}'.format(id)})
