# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_db(app):
    db.init_app(app)


from nbs.models.supplier import Supplier
from nbs.models.contact import Contact, SupplierContact
from nbs.models.hr import Employee, AttendanceRecord
from nbs.models.fiscal import FiscalData
from nbs.models.bank import Bank, BankAccount
from nbs.models.document import (
    PurchaseDocument, PurchaseOrder, PurchaseOrderItem
)
from nbs.models.misc import Address, Email, Phone, ExtraField
