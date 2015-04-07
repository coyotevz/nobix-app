# -*- coding: utf-8 -*-

from flask import jsonify, request
from webargs import Arg
from nbs.models import Supplier
from nbs.schema import SupplierSchema, BankAccountSchema
from nbs.utils.api import ResourceApi, route
from nbs.utils.args import get_args, build_args

s_schema = SupplierSchema()
ba_schema = BankAccountSchema(many=True, exclude=('supplier_id', 'supplier_name'))

patch_args = {
    'leap_time': Arg(int, allow_missing=True),
    'payment_term': Arg(int, allow_missing=True),
}

class SupplierApi(ResourceApi):
    route_base = 'suppliers'

    def index(self):
        """
        Returns a paginated list of suppliers that match with the given
        conditions.
        """
        q = Supplier.query
        return jsonify(objects=s_schema.dump(q, many=True).data)

    @route('/<int:id>')
    def get(self, id):
        """Returns an individual supplier given an id"""
        supplier = Supplier.query.get_or_404(id)
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
        return jsonify({'action': 'POST'})

    @route('/<int:id>', methods=['PATCH'])
    def patch(self, id):
        args = get_args(patch_args)
        args['action'] = 'PATCH {0}'.format(id)
        return jsonify(args)

    def delete(self, id):
        return jsonify({'action': 'DELETE {0}'.format(int(id))})

    @route('<int:id>/accounts')
    def accounts(self, id):
        supplier = Supplier.query.get_or_404(id)
        return jsonify(objects=ba_schema.dump(supplier.bank_accounts).data)
