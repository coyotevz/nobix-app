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


class BankAccountType(db.Model):
    __tablename__ = 'bank_account_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True, nullable=False)
    abbr = db.Column(db.Unicode)


class BankAccount(db.Model):
    __tablename__ = 'bank_account'

    id = db.Column(db.Integer, primary_key=True)
    bank_branch = db.Column(db.Unicode)

    type_id = db.Column(db.ForeignKey('bank_account_type.id'))
    type = db.relationship(BankAccountType)

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

    def __repr__(self):
        return "<BankAccount '{}, {}: {}' of '{}'>".format(
            self.bank.name, self.type.name, self.number,
            self.supplier.name
        )
