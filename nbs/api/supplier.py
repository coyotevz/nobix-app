# -*- coding: utf-8 -*-

from flask import jsonify, request
from webargs import Arg
from nbs.models import Supplier
from nbs.schema import SupplierSchema, BankAccountSchema
from nbs.utils.api import ResourceApi, NestedApi, route
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

    def _get_obj(self, id):
        return Supplier.query.get_or_404(int(id))

    def index(self):
        """
        Returns a paginated list of suppliers that match with the given
        conditions.
        """
        q = Supplier.query
        return jsonify(objects=s_schema.dump(q, many=True).data)

    def get(self, id):
        """Returns an individual supplier given an id"""
        supplier = self._get_obj(id)
        return jsonify(s_schema.dump(supplier).data)

    @route('/<rangelist:ids>')
    def get_many(self, ids):
        suppliers = []
        for id in ids:
            s = Supplier.query.get(id)
            if s is not None:
                suppliers.append(s)
        return jsonify(objects=s_schema.dump(suppliers, many=True).data)

    def post(self):
        args = get_args(post_args)
        args['action'] = 'POST'
        return jsonify(args)

    def patch(self, id):
        args = get_args(patch_args)
        args['action'] = 'PATCH {0}'.format(int(id))
        return jsonify(args)

    def delete(self, id):
        return jsonify({'action': 'DELETE {0}'.format(int(id))})

    test_accounts = NestedApi(BankAccountApi, '<id>')

    @route('<id>/accounts')
    def accounts(self, id):
        #supplier = Supplier.query.get_or_404(int(id))
        supplier = self._get_obj(id)
        return jsonify(objects=ba_schema.dump(supplier.bank_accounts).data)
