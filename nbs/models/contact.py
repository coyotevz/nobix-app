# -*- coding: utf-8 -*-

from nbs.models import db
from nbs.models.entity import Entity


class Contact(Entity):
    __tablename__ = 'contact'
    __mapper_args__ = {'polymorphic_identity': 'contact'}

    contact_id = db.Column(db.Integer, db.ForeignKey('entity.id'),
                           primary_key=True)
    first_name = Entity._name_1
    last_name = Entity._name_2



class SupplierContact(db.Model):
    __tablename__ = 'supplier_contact'
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'),
                            primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.contact_id'),
                           primary_key=True)
    role = db.Column(db.Unicode)

    #: 'supplier' attribute is added by Supplier.supplier_contacts relation

    contact = db.relationship(Contact, lazy='joined',
                              backref='supplier_contacts')

    def __init__(self, contact, role):
        self.contact = contact
        self.role = role

    def __repr__(self):
        return "<SupplierContact {0}, {1}, {2}>".format(
            self.supplier.name.encode('utf-8'),
            self.role.encode('utf-8'),
            self.contact.full_name.encode('utf-8')
        )
