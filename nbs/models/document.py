# -*- coding: utf-8 -*-

from nbs.models import db
from nbs.models.misc import TimestampMixin


class PurchaseDocument(db.Model, TimestampMixin):
    __tablename__ = 'purchase_document'
    __table_args__ = (
        db.UniqueConstraint('pos_no', 'number', 'supplier_id'),
    )

    TYPE_FACTURA_A = 'TYPE_FACTURA_A'
    TYPE_PRESUPUESTO = 'TYPE_PRESUPUESTO'

    _doc_type = {
        TYPE_FACTURA_A: 'Factura A',
        TYPE_PRESUPUESTO: 'Presupuesto',
    }

    STATUS_PENDING = 'STATUS_PENDING'
    STATUS_EXPIRED = 'STATUS_EXPIRED'
    STATUS_PAID = 'STATUS_PAID'

    _doc_status = {
        STATUS_PENDING: 'Pendiente',
        STATUS_EXPIRED: 'Vencida',
        STATUS_PAID: 'Pagada',
    }

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.Enum(*_doc_type.keys(), name='doc_type'),
                              default=TYPE_FACTURA_A)

    #: invoice point of sale number
    pos_no = db.Column(db.Integer, nullable=True)
    number = db.Column(db.Integer, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    issue_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    status = db.Column(db.Enum(*_doc_status.keys(), name='doc_status'),
                       default=STATUS_PENDING)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'),
                            nullable=False)
    supplier = db.relationship('Supplier', backref=db.backref('documents',
                                                              lazy='dynamic'))

    @property
    def type_str(self):
        return self._doc_type[self.document_type]

    @property
    def status_str(self):
        return self._doc_status[self.status]

    @property
    def number_display(self):
        retval = "%08d" % self.document_number
        if self.pos_no:
            retval = "%04d-%s" % (self.pos_no, retval)
        return retval


class PurchaseOrder(db.Model, TimestampMixin):
    __tablename__ = 'purchase_order'

    STATUS_CANCELLED = 'STATUS_CANCELLED'
    STATUS_QUOTING   = 'STATUS_QUOTING'
    STATUS_PENDING   = 'STATUS_PENDING'
    STATUS_PARTIAL   = 'STATUS_PARTIAL'
    STATUS_CONFIRMED = 'STATUS_CONFIRMED'
    STATUS_CLOSED    = 'STATUS_CLOSED'
    STATUS_DRAFT     = 'STATUS_DRAFT'

    _order_status = {
        STATUS_CANCELLED: 'Cancelada',
        STATUS_QUOTING: 'Presupuestando',
        STATUS_PENDING: 'Pendiente',
        STATUS_PARTIAL: 'Parcial',
        STATUS_CONFIRMED: 'Confirmada',
        STATUS_CLOSED: 'Cerrada',
        STATUS_DRAFT: 'Borrador',
    }

    NOTIFY_EMAIL      = 'NOTIFY_EMAIL'
    NOTIFY_FAX        = 'NOTIFY_FAX'
    NOTIFY_PHONE      = 'NOTIFY_PHONE'
    NOTIFY_PERSONALLY = 'NOTIFY_PERSONALLY'

    _notify = {
        NOTIFY_EMAIL: 'Correo Electrónico',
        NOTIFY_FAX: 'Fax',
        NOTIFY_PHONE: 'Telefónico',
        NOTIFY_PERSONALLY: 'Personalmente',
    }

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    issue_date = db.Column(db.DateTime)
    notes = db.Column(db.UnicodeText)
    status = db.Column(db.Enum(*_order_status.keys(), name='order_status'),
                       default=STATUS_DRAFT)
    notify = db.Column(db.Enum(*_notify.keys(), name='notify'),
                       default=NOTIFY_EMAIL)

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'))
    supplier = db.relationship('Supplier',
                               backref=db.backref('orders', lazy='dynamic'))

    def add_item(self, item, position=None):
        assert isinstance(item, PurchaseOrderItem)
        if position is not None and position <= self.items.count():
            position = max(position, 1)
            self.reindex_items(position, 1)
            item.order_index = position
        else:
            item.order_index = self.items.count() + 1
        self.items.append(item)

    def reindex_items(self, start=1, shift=0):
        items = self.items.filter(PurchaseOrderItem.order_index>=start).all()
        for idx, item in reversed(list(enumerate(items, start=(start+shift)))):
            # This modifies unique key so do in subtransactions
            with db.session.begin(subtransactions=True):
                item.order_index = idx

    @property
    def status_str(self):
        return self._order_status[self.status]

    @property
    def notify_str(self):
        return self._notify[self.notify]


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_orderitem'
    __table_args__ = (
        db.UniqueConstraint('order_index', 'order_id'),
        db.UniqueConstraint('sku', 'order_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Unicode) # codigo producto
    description = db.Column(db.Unicode)
    quantity = db.Column(db.Integer, nullable=False)
    received_quantity = db.Column(db.Integer, default=0)

    order_index = db.Column(db.Integer, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'),
                         nullable=False)
    order = db.relationship(PurchaseOrder,
                            backref=db.backref('items', lazy='dynamic',
                                               order_by=order_index))
    def __repr__(self):
        return "<PurchaseOrderItem {} '{} {} * {}' of PO{}>".format(
                self.order_index, self.sku, self.description, self.quantity,
                self.order.number)
