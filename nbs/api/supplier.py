# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify, url_for
from webargs.flaskparser import parser
from marshmallow import Schema, fields, post_load, validates, ValidationError
from marshmallow.validate import Length

from nbs.models import db, Supplier
from nbs.utils.api import build_result


class SupplierSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=[Length(min=2)])

    @validates('name')
    def validate_unique_name(self, value):
        exists = Supplier.query.filter(Supplier.name==value).first()
        if exists is not None:
            raise ValidationError('Supplier name must be unique',
                                  status_code=409)

    @post_load
    def make_supplier(self, data):
        return Supplier(**data)

    class Meta:
        strict = True


supplier_api = Blueprint('api.supplier', __name__, url_prefix='/api/suppliers')

supplier_schema = SupplierSchema()


@supplier_api.route('')
def get_suppliers():
    """
    Returns a paginated list of suppliers that match with the given conditions.
    """
    return build_result(Supplier.query.order_by(Supplier.name), supplier_schema)

@supplier_api.route('/<int:id>')
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    return build_result(supplier, supplier_schema)

@supplier_api.route('/<rangelist:ids>')
def get_suppliers_range(ids):
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
    return '', 201, {'Location': url_for('.get_supplier', id=supplier.id, _external=True)}
