# -*- coding: utf-8 -*-

from sqlalchemy.ext.associationproxy import association_proxy

from nbs.models import db
from nbs.models.entity import Entity


class Supplier(Entity):
    __tablename__ = 'supplier'
    __mapper_args__ = {'polymorphic_identity': u'supplier'}

    FREIGHT_SUPPLIER = 'FREIGHT_SUPPLIER'
    FREIGHT_CUSTOMER = 'FREIGHT_CUSTOMER'

    _freight_types = {
        FREIGHT_SUPPLIER: 'Flete de proveedor',
        FREIGHT_CUSTOMER: 'Flete de cliente',
    }

    supplier_id = db.Column(db.Integer, db.ForeignKey('entity.id'),
                            primary_key=True)
    name = Entity._name_1

    fiscal_data_id = db.Column(db.Integer, db.ForeignKey('fiscal_data.id'))
    fiscal_data = db.relationship('FiscalData',
                                  backref=db.backref('supplier',
                                                     uselist=False))

    #: our number as customer with this supplier
    customer_no = db.Column(db.Unicode)
    payment_term = db.Column(db.Integer) # in days
    freight_type = db.Column(db.Enum(*_freight_types.keys(),
                             name='freight_type'), default=FREIGHT_CUSTOMER)
    leap_time = db.Column(db.Integer) # in days

    supplier_contacts = db.relationship('SupplierContact',
                                        cascade='all,delete-orphan',
                                        backref='supplier')
    contacts = association_proxy('supplier_contacts', 'contact')

    #: 'bank_accounts' attribute added by BankAccount.supplier relation

    @property
    def freight_type_str(self):
        return self._freight_types[self.freight_type]

    def add_contact(self, contact, role):
        self.supplier_contacts.append(SupplierContact(contact, role))
