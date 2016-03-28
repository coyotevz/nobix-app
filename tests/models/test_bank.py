# -*- coding: utf-8 -*-

from pytest import raises
from sqlalchemy.exc import IntegrityError

from tests import DBTestCase
from nbs.models.bank import Bank, BankAccountType


class TestBank(DBTestCase):

    def test_required_name(self):
        b = Bank()
        self.add(b)
        with raises(IntegrityError):
            self.commit()

    def test_unique_name(self):
        b1 = Bank(name='b')
        b2 = Bank(name='b')
        self.add_all([b1, b2])
        with raises(IntegrityError):
            self.commit()

    def test_bcra_code(self):
        b1 = Bank(name='a', bcra_code='0043')
        self.add_commit(b1)
        assert b1.bcra_code == '0043'

    def test_valid_cuit(self):
        b1 = Bank(name='bna', cuit='30500010912')
        self.add_commit(b1)
        assert b1.cuit == '30500010912'

    def test_invalid_cuit(self):
        with raises(ValueError):
            b1 = Bank(name='bna', cuit='30500010312')

    def test_invalid_cuit_after_creation(self):
        b1 = Bank(name='bna')
        self.add_commit(b1)
        with raises(ValueError):
            b1.cuit = '30500010312'

class TestBankAccountType(DBTestCase):

    def test_required_name(self):
        acc = BankAccountType()
        self.add(acc)
        with raises(IntegrityError):
            self.commit()

    def test_unique_name(self):
        a1 = BankAccountType(name='a')
        a2 = BankAccountType(name='a')
        self.add_all([a1, a2])
        with raises(IntegrityError):
            self.commit()

    def test_optional_abbr(self):
        acc = BankAccountType(name='acc_type')
        self.add_commit(acc)
        assert acc.name == 'acc_type'
        assert acc.abbr is None

    def test_abbr(self):
        acc = BankAccountType(name='acc_type', abbr='AT')
        self.add_commit(acc)
        assert acc.name == 'acc_type'
        assert acc.abbr == 'AT'
