# -*- coding: utf-8 -*-

from flask import jsonify, request
from webargs import Arg
from nbs.models import Supplier
from nbs.schema import SupplierSchema, BankAccountSchema
from nbs.utils.api import ResourceApi, NestedApi, route, build_result
from nbs.utils.args import get_args, build_args
from nbs.api.bank_account import BankAccountApi

s_schema = SupplierSchema()
ba_schema = BankAccountSchema(many=True, exclude=('supplier_id', 'supplier_name'))

writable_schema = SupplierSchema(
    exclude=('id', 'full_name', 'modified', 'created')
)

patch_args = build_args(writable_schema, allow_missing=True)
post_args = build_args(writable_schema)

class SupplierApi(ResourceApi):
    route_base = 'suppliers'

    @classmethod
    def get_obj(cls, id):
        return Supplier.query.get_or_404(id)

    def index(self):
        """
        Returns a paginated list of suppliers that match with the given
        conditions.
        """
        return build_result(Supplier.query, s_schema)

    @route('<int:id>')
    def get(self, id):
        """Returns an individual supplier given an id"""
        supplier = self.get_obj(id)
        return build_result(supplier, s_schema)

    @route('/<rangelist:ids>')
    def get_many(self, ids):
        suppliers = []
        for id in ids:
            s = Supplier.query.get(id)
            if s is not None:
                suppliers.append(s)
        return build_result(suppliers, s_schema)

    def post(self):
        args = get_args(post_args)
        args['action'] = 'POST'
        return jsonify(args)

    @route('<int:id>', methods=['PATCH'])
    def patch(self, id):
        args = get_args(patch_args)
        args['action'] = 'PATCH {0}'.format(id)
        return jsonify(args)

    @route('<int:id>', methods=['DELETE'])
    def delete(self, id):
        return jsonify({'action': 'DELETE {0}'.format(id)})

    accounts = NestedApi(BankAccountApi, pk_converter='int')
