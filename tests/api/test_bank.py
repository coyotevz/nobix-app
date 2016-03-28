# -*- coding: utf-8 -*-

from tests import APITestCase
from nbs.models.bank import Bank, BankAccountType


class TestBank(APITestCase):

    def test_initial_empty_list(self):
        rv, data = self.get('/api/banks')
        assert rv.status_code == 200
        assert data['num_results'] == 0
        assert len(data['objects']) == 0

    def test_new_bank(self):
        rv, data = self.post('/api/banks', data={'name': 'b1'})
        assert rv.status_code == 201
        assert list(data.keys()) == ['id']

        b = Bank.query.get(data['id'])
        assert b.name == 'b1'
        assert b.bcra_code is None
        assert b.cuit is None


class TestBankAccountType(APITestCase):

    def test_initial_empty_list(self):
        rv, data = self.get('/api/banks/account_types')
        assert rv.status_code == 200
        assert data['num_results'] == 0
        assert len(data['objects']) == 0

    def test_new_account_type(self):
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'acc_type'})
        assert rv.status_code == 201
        assert list(data.keys()) == ['id']

        acc = BankAccountType.query.get(data['id'])
        assert acc.name == 'acc_type'
        assert acc.abbr is None

    def test_new_account_type_with_abbr(self):
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'acc_type', 'abbr': 'AT'})
        assert rv.status_code == 201

        acc = BankAccountType.query.get(data['id'])
        assert acc.name == 'acc_type'
        assert acc.abbr == 'AT'

    def test_new_account_type_ignore_bad_args(self):
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'acc_type', 'bad_arg': 5})
        assert rv.status_code == 201
        assert list(data.keys()) == ['id']

    def test_name_min_length(self):
        rv, data = self.post('/api/banks/account_types', data={'name': 'a'})
        assert rv.status_code == 422
        assert data['messages']['name'] == ["Shorter than minimum length 2."]

    def test_unique_name(self):
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'acc_type'})
        assert rv.status_code == 201
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'acc_type'})
        assert rv.status_code == 422
        assert data['messages']['name'] == \
                ["BankAccountType name must be unique."]

    def test_unique_abbr(self):
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'acc_type', 'abbr': 'AT'})
        assert rv.status_code == 201
        rv, data = self.post('/api/banks/account_types',
                             data={'name': 'ac_type', 'abbr': 'AT'})
        assert rv.status_code == 422
        assert data['messages']['abbr'] == \
                ["BankAccountType abbr must be unique."]

    def test_get_fields(self):
        a1 = BankAccountType(name='a1', abbr='A1')
        a2 = BankAccountType(name='a2', abbr='A2')
        a3 = BankAccountType(name='a3')
        self.db.session.add_all([a1, a2, a3])
        self.db.session.commit()

        rv, data = self.get('/api/banks/account_types')
        assert rv.status_code == 200
        assert data['objects'] == [
            {'id': 1, 'name': 'a1', 'abbr': 'A1'},
            {'id': 2, 'name': 'a2', 'abbr': 'A2'},
            {'id': 3, 'name': 'a3', 'abbr': None}
        ]
