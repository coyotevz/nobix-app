# -*- coding: utf-8 -*-

from tests import APITestCase
from nbs.models.bank import Bank, BankAccountType


class TestBank(APITestCase):

    def test_initial_empty_list(self):
        rv, data = self.get('/api/banks')
        assert rv.status_code == 200
        assert data['num_results'] == 0
        assert len(data['objects']) == 0


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
        assert rv.status_code == 201
