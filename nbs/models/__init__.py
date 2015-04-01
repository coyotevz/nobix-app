# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_db(app):
    db.init_app(app)


from nbs.models.supplier import (
    Supplier, Contact, SupplierContact, FiscalData, Bank, BankAccount
)
from nbs.models.misc import Address, Email, Phone, ExtraField
