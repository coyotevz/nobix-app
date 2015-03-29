# -*- coding: utf-8 -*-

from nbs.models import db
from nbs.models.entity import Entity
from nbs.models.misc import FiscalDataMixin


class Supplier(Entity, FiscalDataMixin):
    __tablename__ = 'supplier'
    __mapper_args__ = {'polymorphic_identity': u'supplier'}

    supplier_id = db.Column(db.Integer, db.ForeignKey('entity.id'),
                            primary_key=True)
    name = Entity._name_1
    fancy_name = Entity._name_2

    payment_term = db.Column(db.Integer)

    @property
    def full_name(self):
        fn = u" ({0})".format(self.fancy_name) if self.fancy_name else u""
        return u"{0}{1}".format(self.name, fn)
