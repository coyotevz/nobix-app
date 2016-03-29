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
        if not validate_cuit(cuit):
            raise ValueError("CUIT invalid")
        return cuit

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

    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'))
    entity = db.relationship('Entity', backref='bank_accounts')

    @validates('cbu')
    def cbu_is_valid(self, key, cbu):
        if not validate_cbu(cbu):
            raise ValueError("CBU invalid")
        return cbu

    def __repr__(self):
        return "<BankAccount '{}, {}: {}' of '{}'>".format(
            self.bank.name, self.type.name, self.number,
            self.entity
        )
