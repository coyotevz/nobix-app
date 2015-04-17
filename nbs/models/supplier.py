# -*- coding: utf-8 -*-

from sqlalchemy.ext.associationproxy import association_proxy

from nbs.models import db
from nbs.models.entity import Entity


class Supplier(Entity):
    __tablename__ = 'supplier'
    __mapper_args__ = {'polymorphic_identity': u'supplier'}

    FREIGHT_SUPPLIER = 'FREIGHT_SUPPLIER'
    FREIGHT_CUSTOMER = 'FREIGHT_CUSTOMER'

    _freight_types = {
        FREIGHT_SUPPLIER: 'Flete de proveedor',
        FREIGHT_CUSTOMER: 'Flete de cliente',
    }

    supplier_id = db.Column(db.Integer, db.ForeignKey('entity.id'),
                            primary_key=True)
    name = Entity._name_1

    fiscal_data_id = db.Column(db.Integer, db.ForeignKey('fiscal_data.id'))
    fiscal_data = db.relationship('FiscalData',
                                  backref=db.backref('supplier',
                                                     uselist=False))

    #: our number as customer with this supplier
    customer_no = db.Column(db.Unicode)
    payment_term = db.Column(db.Integer) # in days
    freight_type = db.Column(db.Enum(*_freight_types.keys(),
                             name='freight_type'), default=FREIGHT_CUSTOMER)
    leap_time = db.Column(db.Integer) # in days

    supplier_contacts = db.relationship('SupplierContact',
                                        cascade='all,delete-orphan',
                                        backref='supplier')
    contacts = association_proxy('supplier_contacts', 'contact')

    #: 'bank_accounts' field added by BankAccount model

    @property
    def freight_type_str(self):
        return self._freight_types[self.freight_type]

    def add_contact(self, contact, role):
        self.supplier_contacts.append(SupplierContact(contact, role))


class PurchaseDocument(db.Model):
    __tablename__ = 'purchase_document'

    TYPE_FACTURA_A = 'TYPE_FACTURA_A'
    TYPE_PRESUPUESTO = 'TYPE_PRESUPUESTO'

    _doc_type = {
        TYPE_FACTURA_A: 'Factura A',
        TYPE_PRESUPUESTO: 'Presupuesto',
    }

    STATUS_PENDING = 'STATUS_PENDING'
    STATUS_EXPIRED = 'STATUS_EXPIRED'
    STATUS_PAID = 'STATUS_PAID'

    _doc_status = {
        STATUS_PENDING: 'Pendiente',
        STATUS_EXPIRED: 'Vencida',
        STATUS_PAID: 'Pagada',
    }

    id = db.Column(db.Integer, primary_key=True)
    document_type = db.Column(db.Enum(*_doc_type.keys(), name='doc_type'),
                              default=TYPE_FACTURA_A)

    #: invoice point of sale number
    pos_no = db.Column(db.Integer)
    number = db.Column(db.Integer)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    issue_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    status = db.Column(db.Enum(*_doc_status.keys(), name='doc_status'),
                       default=STATUS_PENDING)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'),
                            nullable=False)
    supplier = db.relationship(Supplier, backref=db.backref('documents',
                                                            lazy='dynamic'))

    @property
    def type_str(self):
        return self._doc_type[self.document_type]

    @property
    def status_str(self):
        return self._doc_status[self.status]

    @property
    def number_display(self):
        retval = "%08d" % self.document_number
        if self.pos_no:
            retval = "%04d-%s" % (self.pos_no, retval)
        return retval


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
    #: 'bank_accounts' attribute added by BankAccount.supplier relation

    contact = db.relationship('Contact', lazy='joined',
                              backref='supplier_contacts')

    def __init__(self, contact, role):
        self.contact = contact
        self.role = role

    def __rpr__(self):
        return "<SupplierContact {0}, {1}, {2}>".format(
            self.supplier.name.encode('utf-8'),
            self.role.encode('utf-8'),
            self.contact.full_name.encode('utf-8')
        )


class FiscalData(db.Model):
    __tablename__ = 'fiscal_data'

    FISCAL_CONSUMIDOR_FINAL = 'FISCAL_CONSUMIDOR_FINAL'
    FISCAL_RESPONSABLE_INSCRIPTO = 'FISCAL_RESPONSABLE_INSCRIPTO'
    FISCAL_EXCENTO = 'FISCAL_EXCENTO'
    FISCAL_MONOTRIBUTO = 'FISCAL_MONOTRIBUTO'

    _fiscal_types = {
        FISCAL_CONSUMIDOR_FINAL: 'Consumidor Final',
        FISCAL_RESPONSABLE_INSCRIPTO: 'Responsable Inscripto',
        FISCAL_EXCENTO: 'Excento',
        FISCAL_MONOTRIBUTO: 'Monotributo',
    }

    id = db.Column(db.Integer, primary_key=True)
    cuit = db.Column(db.Unicode(13))
    fiscal_type = db.Column(db.Enum(*_fiscal_types.keys(),
                                    name='fiscal_type_enum'),
                            default=FISCAL_CONSUMIDOR_FINAL)

    @property
    def fiscal_type_str(self):
        return self._fiscal_types.get(self.fiscal_type, 'Unknown')

    @property
    def needs_cuit(self):
        return self.fiscal_type in (self.FISCAL_EXCENTO,
                                    self.FISCAL_RESPONSABLE_INSCRIPTO)

    def __repr__(self):
        return "<FiscaData '{} {}' of '{}'>".format(
                self.fiscal_type_str,
                self.cuit,
                self.supplier.name
        )


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

    _account_type = {
        TYPE_CC_PESOS: 'Cuenta Corriente en Pesos',
        TYPE_CC_USD: 'Cuenta Corriente en Dólares',
        TYPE_CA_PESOS: 'Caja de Ahorro en Pesos',
        TYPE_CA_USD: 'Caja de Ahorro en Dólares',
        TYPE_UNIQUE: 'Cuenta Única',
    }


    id = db.Column(db.Integer, primary_key=True)
    bank_branch = db.Column(db.Unicode)
    account_type = db.Column(db.Enum(*_account_type.keys(),
                             name='account_type'), default=TYPE_CC_PESOS)
    account_number = db.Column(db.Unicode)
    account_cbu = db.Column(db.Unicode)
    account_owner = db.Column(db.Unicode)


    bank_id = db.Column(db.Integer, db.ForeignKey('bank.id'), nullable=False)
    bank = db.relationship(Bank, backref="accounts")

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.supplier_id'))
    supplier = db.relationship(Supplier, backref='bank_accounts')

    @property
    def account_type_str(self):
        return self._account_type[self.account_type]

    def __repr__(self):
        return "<BankAccount '{}, {}: {}' of '{}'>".format(
            self.bank.name, self.account_type_str, self.account_number,
            self.supplier.name
        )
