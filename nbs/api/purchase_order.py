# -*- coding: utf-8 -*-

from flask import jsonify, url_for, abort
from nbs.models import db, PurchaseOrder, PurchaseOrderItem
from nbs.schema import PurchaseOrderSchema, PurchaseOrderItemSchema
from nbs.utils.api import ResourceApi, route, build_result
from nbs.utils.args import get_args, build_args


po_schema = PurchaseOrderSchema()


class PurchaseOrderApi(ResourceApi):
    route_base = 'purchase_order'

    def index(self):
        q = PurchaseOrder.query
        if self.obj:
            q = q.filter(PrucaseOrder.supplier==self.obj)
        return build_result(q, po_schema)

    @route('<int:id>')
    def get(self, id):
        po = PurchaseOrder.query.get_or_404(id)
        if self.obj:
            if not po.supplier == self.obj:
                abort(404)
        return build_result(po, po_schema)
