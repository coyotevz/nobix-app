# -*- coding: utf-8 -*-

from flask import jsonify, request, url_for
from nbs.models import db, Supplier
from nbs.schema import SupplierSchema, BankAccountSchema
from nbs.utils.api import ResourceApi, NestedApi, route, build_result
from nbs.utils.args import get_args, build_args, Arg, ValidationError
from nbs.api.bank_account import BankAccountApi

s_schema = SupplierSchema()
ba_schema = BankAccountSchema(many=True,
                              exclude=('supplier_id', 'supplier_name'))

writable_schema = SupplierSchema(
    exclude=('id', 'modified', 'created')
)

def unique_supplier_name(val):
    exists = Supplier.query.filter(Supplier.name==val).first()
    if exists is not None:
        raise ValidationError('Supplier name must be unique', status_code=409)

post_args = build_args(writable_schema, allow_missing=True)
post_args['name'] = Arg(str, required=True, validate=unique_supplier_name)

patch_args = build_args(writable_schema, allow_missing=True)

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
        supplier, e = writable_schema.load(args)
        db.session.add(supplier)
        db.session.commit()
        return '', 201, {'Location': url_for('.get', id=supplier.id,
                                             _external=True)}
        return build_result(supplier, s_schema), 201

    @route('<int:id>', methods=['PATCH'])
    def patch(self, id):
        supplier = Supplier.query.get_or_404(id)
        args = get_args(patch_args)
        print('args:', args)
        for k, v in args.items():
            setattr(supplier, k, v)
        db.session.commit()
        return '', 204

    @route('<int:id>', methods=['DELETE'])
    def delete(self, id):
        supplier = Supplier.query.get_or_404(id)
        db.session.delete(supplier)
        db.session.commit()
        return '', 204

    def freight_types(self):
        return jsonify(**Supplier._freight_types)

    accounts = NestedApi(BankAccountApi, pk_converter='int')
