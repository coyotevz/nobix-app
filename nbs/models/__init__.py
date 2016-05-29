# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def configure_db(app):
    db.init_app(app)

from nbs.models.entity import Entity
from nbs.models.misc import Address, Email, Phone, ExtraField
from nbs.models.bank import Bank, BankAccount, BankAccountType
