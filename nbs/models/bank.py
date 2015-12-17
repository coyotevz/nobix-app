# -*- coding: utf-8 -*-

from nbs.models import db


class Bank(db.Model):
    __tablename__ = 'bank'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    # TODO: Add bank logo, to quickly identify

    def __repr__(self):
        return "<Bank '{}'>".format(self.name)


class BankAccount(db.Model):
    __tablename__ = 'bank_account'

    TYPE_CC_PESOS = 'TYPE_CC_PESOS'
    TYPE_CC_USD = 'TYPE_CC_USD'
    TYPE_CA_PESOS = 'TYPE_CA_PESOS'
    TYPE_CA_USD = 'TYPE_CA_USD'
    TYPE_UNIQUE = 'TYPE_UNIQUE'

    _account_types = {
        TYPE_CC_PESOS: 'Cuenta Corriente en Pesos',
        TYPE_CC_USD: 'Cuenta Corriente en Dólares',
        TYPE_CA_PESOS: 'Caja de Ahorro en Pesos',
        TYPE_CA_USD: 'Caja de Ahorro en Dólares',
        TYPE_UNIQUE: 'Cuenta Única',
    }


    id = db.Column(db.Integer, primary_key=True)
    bank_branch = db.Column(db.Unicode)
    account_type = db.Column(db.Enum(*_account_types.keys(),
                             name='account_type'), default=TYPE_CC_PESOS)
    account_number = db.Column(db.Unicode)
    account_cbu = db.Column(db.Unicode)
    account_owner = db.Column(db.Unicode)


    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=False)
    bank = db.relationship(Bank, backref="accounts")

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'))
    supplier = db.relationship('Supplier', backref='bank_accounts')

    @property
    def account_type_str(self):
        return self._account_type[self.account_type]

    def __repr__(self):
        return "<BankAccount '{}, {}: {}' of '{}'>".format(
            self.bank.name, self.account_type_str, self.account_number,
            self.supplier.name
        )
