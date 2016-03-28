# -*- coding: utf-8 -*-

from sqlalchemy.orm import validates

from nbs.models import db
from nbs.utils.validators import validate_cuit, validate_cbu


class Bank(db.Model):
    __tablename__ = 'bank'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True, nullable=False)
    bcra_code = db.Column(db.Unicode(8))
    cuit = db.Column(db.Unicode(11))
    # TODO: Add bank logo, to quickly identify

    @validates('cuit')
    def cuit_is_valid(self, key, cuit):
        assert validate_cuit(cuit)

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
    type = db.Column(db.Enum(*_account_types.keys(),
                     name='account_types'), default=TYPE_CC_PESOS)
    number = db.Column(db.Unicode)
    cbu = db.Column(db.Unicode)
    owner = db.Column(db.Unicode)

    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=False)
    bank = db.relationship(Bank, backref="accounts")

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'))
    supplier = db.relationship('Supplier', backref='bank_accounts')

    @validates('cbu')
    def cbu_is_valid(self, key, cbu):
        assert validate_cbu(cbu)

    @property
    def account_type_str(self):
        return self._account_types[self.account_type]

    def __repr__(self):
        return "<BankAccount '{}, {}: {}' of '{}'>".format(
            self.bank.name, self.account_type_str, self.account_number,
            self.supplier.name
        )
