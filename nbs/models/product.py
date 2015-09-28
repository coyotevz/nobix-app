# -*- coding: utf-8 -*-

from datetime import datetime
from nbs.models import db
from nbs.models.misc import TimestampMixin


class ProductCategory(db.Model):
    __tablename__ = 'product_category'

    id = db.Column(db.Integer, primary_key=True)

    #: category name
    name = db.Column(db.Unicode, nullable=False)

    #: category description
    name = db.Column(db.Unicode)

    #: suggested markup components for calculating the product's price
    #suggested_markup_components = db.relationship('PriceComponent',
    #        backref=db.backref('category_markup', lazy='dynamic'),
    #        secondary=lambda: productcategory_pricecomponent)

    #: a saleman suggested commission for products of this category.
    suggested_commission = db.Column(db.Numeric(10, 5))

    parent_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    parent = db.relationship('ProductCategory', backref='children',
                             remote_side=[id])

    def get_commission(self):
        """
        Returns the commission for this category.
        If it's unset, return the value of the base category, if any.
        """
        return self.suggested_commission or self.parent and self.parent.get_commision()

    def get_markup(self):
        """
        Returns the markup for this category.
        If it's unset, return the value of the base category, if any.
        """
        if len(self.suggested_markup_components):
            for mc in self.suggested_markup_components:
                yield mc.value
        elif self.parent:
            return self.parent.get_markup()
        return


class Product(db.Model, TimestampMixin):
    __tablename__ = 'product'

    #: the product is available and can be used on a |purchase|/|sale|
    STATUS_AVAILABLE = 'STATUS_AVAILABLE'

    #: the product is closed, that is, it still exists for references,
    #: but it should not be possible to create |purchase|/|sale| with it
    STATUS_CLOSED = 'STATUS_CLOSED'

    #: the product is suspended, that is, it still exists for future refereces
    #: but it should not be possible to create a |purchase|/|sale| with it
    #: until back to available status
    STATUS_SUSPENDED = 'STATUS_SUSPENDED'

    _statuses = {
        STATUS_AVAILABLE: 'Disponible',
        STATUS_CLOSED: 'Cerrado',
        STATUS_SUSPENDED: 'Suspendido',
    }

    TYPE_PERMANENT = 'TYPE_PERMANENT'
    TYPE_ON_REQUEST = 'TYPE_ON_REQUEST'
    TYPE_CONSIGMENT = 'TYPE_CONSIGMENT'

    _product_types = {
        TYPE_PERMANENT: 'Permanente',
        TYPE_ON_REQUEST: 'Bajo Pedido',
        TYPE_CONSIGMENT: 'Consignacion',
    }

    id = db.Column(db.Integer, primary_key=True)

    #: stock keeping unit, for internal identifying the sellable product
    sku = db.Column(db.Unicode(24), index=True, nullable=False, unique=True)

    #: barcode, ussually printed and attached to the package
    barcode = db.Column(db.Unicode(48), unique=True)

    #: description of sellable product
    description = db.Column(db.Unicode(128), nullable=False)

    #: short description (mostly for Fiscal Ticket)
    short_description = db.Column(db.Unicode(40))

    #: notes for this product
    notes = db.Column(db.UnicodeText)

    #: sale price without taxes (can be null, not sellable)
    price = db.Column(db.Numeric(10, 2))

    #: User markup formula to calculate sale price?
    automatic_price = db.Column(db.Boolean, default=False)

    #: cost of this product
    _cost = db.Column('cost', db.Numeric(10, 2))

    #: use ProductSupplierInfo.cost to calculate cost
    automatic_cost = db.Column(db.Boolean, default=False)

    #: saleman commission factor (commission factor x sale price) = commission
    commission = db.Column(db.Numeric(10, 5))

    #: unit of the product, kg, l, etc.
    #unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    #unit = db.relationship('ProductUnit', backref=db.backref('products',
    #                                                         lazy='dynamic'))

    #: category this product belong to
    category_id = db.Column(db.Integer, db.ForeignKey('product_category.id'))
    category = db.relationship('ProductCategory',
                               backref=db.backref('products', lazy='dynamic'))

    #tax_constant_id = db.Column(db.Integer,
    #                            db.ForeignKey('tax_constant.id'))
    #tax_constant = db.relationship('TaxConstant',
    #                               backref=db.backref('products',
    #                                                  lazy='dynamic'))

    status = db.Column(db.Enum(*_statuses.keys(), name='product_status_enum'),
                       default=STATUS_AVAILABLE)

    product_type = db.Column(db.Enum(*_product_types.keys(),
                             name='prodyt_type_enum'), default=TYPE_PERMANENT)

    #: 'created' field added by TimestampMixin
    #: 'modified' field added by TimestampMixin

    #: PriceComponents for automatic price calculation:
    #markup_components = db.relationship('PriceComponent',
    #        backref=db.backref("product_markup", lazy='dynamic'),
    #        secondary=lambda: product_pricecomponent)

    #: 'suppliers_info' field is added by ProductSupplierInfo class
    #: 'images' field is added by ProductImage class
    #: 'stock' field is added by ProductStock class

    #: When calculate the product cost and we have multiple suppliers for the
    #: same product, this field indacates that we need to use this info for
    #: calculus. A product can have only one main_supplier_info.
    #main_supplier_info_id = db.Column(
    #        db.Integer, db.ForeignKey('product_supplier_info.supplier_id',
    #                                  use_alter=True,
    #                                  name='fk_main_supplier_info'))
    #main_supplier_info = db.relationship(
    #    'ProductSupplierInfo',
    #    primaryjoin="and_("
    #        "Product.main_supplier_info_id==ProductSupplierInfo.supplier_id,"
    #        "Product.id==ProductSupplierInfo.product_id)",
    #    foreign_keys=[main_supplier_info_id, id],
    #    post_update=True
    #)

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        """Update product price based on new cost value"""
        if self._cost == value:
            return
        self._cost = value
        # TODO: Recalc product price

    @property
    def status_str(self):
        return self._statuses[self.status]

    @property
    def product_type_str(self):
        return self._product_types[self.product_type]

    def __repr__(self):
        return "<Product({0})>".format(self.sku.encode('utf-8'))

    def increse_stock(self, quantity, warehouse, type, unit_cost=None):
        """
        When receiving a product, update the stock reference for this product
        on a specific warehouse.

        :param quantity: amount to increase
        :param warehouse: warehouse that stores this product stock
        :param type: the type of the stock increase. One of
            StockTransaction.types
        :param unit_cost: unit cost of the new stock or `None`
        """
        assert (type in StockTransaction.types)

        if quantity <= 0:
            raise ValueError('quantity must be a positive integer')
        if warehouse is None:
            raise ValueError('warehouse cannot be `None`')

        stock = self.get_stock_for_warehouse(warehouse)
        stock.increase_stock(quantity, warehouse, type, unit_cost)

    def decrease_stock(self, quantity, warehouse, type):
        """
        When deliver a product, update the stock reference for the sold item on
        specific warehouse. Returns the stock item that was decreased.

        :params quantity: amount to decrease
        :params warehouse: warehouse that stores this stock
        :param type: the type of the stock drecrease. One of
            StockTransaction.types
        """
        assert (type in StockTransaction.types)

        if quantity <= 0:
            raise ValueError('quantity must be a positive integer')
        if warehouse is None:
            raise ValueError('warehouse cannot be `None`')

        stock = self.get_stock_for_warehouse(warehouse)

        if quantity > stock.quantity:
            raise ValueError('quantity to decrease is greater than the '
                             'available stock.')

        stock.decrease_stock(quantity, warehouse, type)
        return stock

    def get_stock_for_warehouse(self, warehouse, create=True):
        """
        Return the stock item for the product in a certain warehouse.
        With create=True if the stock item wasn't exist create one with stock
        quantity 0.

        :params warehouse: warehouse that stores this product
        :params create: default True, must create item if wasn't exist yet
        """
        try:
            return self.stock.filter(ProductStock.warehouse==warehouse).one()
        except NoResultFound:
            if create:
                return ProductStock(product=self, warehouse=warehouse,
                                    quantity=0)
            else:
                return None
