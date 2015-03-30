# -*- coding: utf-8 -*-

from nbs.models import db
from nbs.models.entity import Entity
from nbs.models.misc import FiscalDataMixin


class Supplier(Entity, FiscalDataMixin):
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
    fancy_name = Entity._name_2

    payment_term = db.Column(db.Integer) # in days
    freight_type = db.Column(db.Enum(*_freight_types.keys(),
                             name='freight_type'), default=FREIGHT_CUSTOMER)
    leap_time = db.Column(db.Integer) # in days

    @property
    def full_name(self):
        fn = " ({0})".format(self.fancy_name) if self.fancy_name else u""
        return "{0}{1}".format(self.name, fn)

    @property
    def freight_type_str(self):
        return self._freight_types[self.freight_type]


class Bank(db.Model):
    __tablename__ = 'bank'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    # TODO: Add bank logo, to quickly identify


class BankAccount(db.Model):
    __tablename__ = 'bank_account'

    TYPE_CC_PESOS = 'TYPE_CC_PESOS'
    TYPE_CC_USD = 'TYPE_CC_USD'
    TYPE_CA_PESOS = 'TYPE_CA_PESOS'
    TYPE_CA_USD = 'TYPE_CA_USD'
    TYPE_UNIQUE = 'TYPE_UNIQUE'

    _account_type = {
        TYPE_CC_PESOS: 'Cuenta Corriente en Pesos',
        TYPE_CC_USD: 'Cuenta Corriente en Dólares',
        TYPE_CA_PESOS: 'Caja de Ahorro en Pesos',
        TYPE_CA_USD: 'Caja de Ahorro en Dólares',
        TYPE_UNIQUE: 'Cuenta Única',
    }


    id = db.Column(db.Integer, primary_key=True)
    bank_branch = db.Column(db.Unicode)
    account_type = db.Column(db.Enum(*_account_type.keys(),
                             name='account_type'), default=TYPE_CC_PESOS)
    account_number = db.Column(db.Unicode)
    account_cbu = db.Column(db.Unicode)
    account_owner = db.Column(db.Unicode)


    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'))
    bank = db.relationship(Bank, backref="accounts")

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'))
    supplier = db.relationship(Supplier, backref='bank_accounts')
