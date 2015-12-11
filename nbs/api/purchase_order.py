# -*- coding: utf-8 -*-

from flask import jsonify, url_for, abort
from nbs.models import db, PurchaseOrder, PurchaseOrderItem
from marshmallow import Schema, fields
from nbs.schema import TimestampSchema
from nbs.utils.api import ResourceApi, route, build_result
from nbs.utils.args import get_args, build_args


class PurchaseOrderSchema(TimestampSchema):
    id = fields.Integer()
    number = fields.Integer()
    issue = fields.DateTime(attribute='issue_date')
    notes = fields.String()
    status = fields.String(attribute='status_str')
    notify = fields.String(attribute='notify_str')
    supplier_id = fields.Integer()
    supplier_name = fields.String(attribute='supplier.name')

    items = fields.Nested('PurchaseOrderItemSchema', many=True,
                          exclude=('id', 'order_id'))


class PurchaseOrderItemSchema(Schema):
    id = fields.Integer()
    sku = fields.String()
    description = fields.String()
    quantity = fields.Integer()
    received_quantity = fields.Integer()
    index = fields.Integer(attribute='order_index')
    order_id = fields.Integer()


po_schema = PurchaseOrderSchema()
post_po_schema = PurchaseOrderSchema(exclude=('issue', 'supplier_name'))

class PurchaseOrderApi(ResourceApi):
    route_base = 'purchases/orders'

    post_args = build_args(post_po_schema, allow_missing=True)

    def index(self):
        q = PurchaseOrder.query
        if self.obj:
            q = q.filter(PurchaseOrder.supplier==self.obj)
        return build_result(q, po_schema)

    @route('<int:id>')
    def get(self, id):
        po = PurchaseOrder.query.get_or_404(id)
        if self.obj:
            if not po.supplier == self.obj:
                abort(404)
        return build_result(po, po_schema)

    def post(self):
        args = get_args(self.post_args)
        if self.obj:
            args['supplier_id'] = self.obj.id
        data, errors = post_po_schema.load(args)
        po = PurchaseOrder(**data)
        db.session.add(po)
        db.session.commit()
        return '', 201, {'Location': url_for('.get', pk=self.obj.id, id=po.id,
                                             _external=True)}
