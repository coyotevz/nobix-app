# -*- coding: utf-8 -*-

from pytest import raises
from sqlalchemy.exc import IntegrityError

from tests import DBTestCase
from nbs.models.bank import Bank, BankAccountType


class TestBank(DBTestCase):

    def test_required_name(self):
        b = Bank()
        self.db.session.add(b)
        with raises(IntegrityError):
            self.db.session.commit()

    def test_unique_name(self):
        b1 = Bank(name='b')
        b2 = Bank(name='b')
        self.db.session.add_all([b1, b2])
        with raises(IntegrityError):
            self.db.session.commit()


class TestBankAccountType(DBTestCase):

    def test_required_name(self):
        acc = BankAccountType()
        self.db.session.add(acc)
        with raises(IntegrityError):
            self.db.session.commit()

    def test_unique_name(self):
        a1 = BankAccountType(name='a')
        a2 = BankAccountType(name='a')
        self.db.session.add_all([a1, a2])
        with raises(IntegrityError):
            self.db.session.commit()

    def test_optional_abbr(self):
        acc = BankAccountType(name='acc_type')
        self.db.session.add(acc)
        self.db.session.commit()
        assert acc.name == 'acc_type'
        assert acc.abbr is None
