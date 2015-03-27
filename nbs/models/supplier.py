# -*- coding: utf-8 -*-

from nbs.models import db


class Supplier(db.Model):
    __tablename__ = 'supplier'

    #default_fields = ['name', 'full_desc']
    #hidden_fields = ['payment']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, nullable=False)
    payment = db.Column(db.Integer)

    @property
    def full_desc(self):
        return "{0} {1}".format(self.name, self.payment)
