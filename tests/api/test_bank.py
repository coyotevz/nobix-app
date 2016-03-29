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

    def test_new_bank_unique_name(self):
        bank = {'name': 'bna'}
        rv, data = self.post('/api/banks', data=bank)
        assert rv.status_code == 201
        rv, data = self.post('/api/banks', data=bank)
        assert rv.status_code == 422
        assert data['messages']['name'] == ['Bank name must be unique.']

    def test_new_bank_with_valid_cuit(self):
        bank = {'name': 'bna', 'cuit': '30500010912'}
        rv, data = self.post('/api/banks', data=bank)
        assert rv.status_code == 201

        b = Bank.query.get(data['id'])
        assert b.name == bank['name']
        assert b.cuit == bank['cuit']
        assert b.bcra_code is None

    def test_new_bank_with_invalid_cuit(self):
        bank = {'name': 'bna', 'cuit': '30500010312'}
        rv, data = self.post('/api/banks', data=bank)
        assert rv.status_code == 422
        assert data['messages']['cuit'] == ['CUIT field invalid.']
        assert Bank.query.count() == 0

    def test_new_bank_with_invalid_cuit_length(self):
        bank1 = {'name': 'bna', 'cuit': '3050001091'}
        bank2 = {'name': 'bna', 'cuit': '305000109121'}

        rv, data = self.post('/api/banks', data=bank1)
        assert rv.status_code == 422
        assert data['messages']['cuit'] == ['Length must be 11.']

        rv, data = self.post('/api/banks', data=bank2)
        assert rv.status_code == 422
        assert data['messages']['cuit'] == ['Length must be 11.']

        assert Bank.query.count() == 0

    def test_new_bank_with_bcra_code(self):
        bank = {'name': 'bna', 'bcra_code': '0043'}
        rv, data = self.post('/api/banks', data=bank)
        assert rv.status_code == 201

        b = Bank.query.get(data['id'])
        assert b.name == bank['name']
        assert b.cuit is None
        assert b.bcra_code == bank['bcra_code']


    def test_list_bank(self):
        bnames = [{'name': 'bna1'}, {'name': 'bna2'}, {'name': 'bna3'}]
        banks = [Bank(**d) for d in bnames]
        self.db.session.add_all(banks)
        self.db.session.commit()

        rv, data = self.get('/api/banks')
        assert rv.status_code == 200
        assert data['num_results'] == 3
        assert len(data['objects']) == 3

        assert data['objects'] == [
            {'id': 1, 'name': 'bna1', 'bcra_code': None, 'cuit': None},
            {'id': 2, 'name': 'bna2', 'bcra_code': None, 'cuit': None},
            {'id': 3, 'name': 'bna3', 'bcra_code': None, 'cuit': None}
        ]

    def test_update_bank(self):
        b = Bank(name='bna', cuit='30500010912')
        self.db.session.add(b)
        self.db.session.commit()

        rv, data = self.get('/api/banks')
        assert rv.status_code == 200
        assert data['num_results'] == 1

        rv, data = self.patch('/api/banks/{}'.format(b.id),
                              data={'name': 'bnb'})
        assert rv.status_code == 204
        assert b.name == 'bnb'

    def test_update_invalid_cuit(self):
        b = Bank(name='bna', cuit='30500010912')
        self.db.session.add(b)
        self.db.session.commit()

        rv, data = self.get('/api/banks')
        assert rv.status_code == 200
        assert data['num_results'] == 1

        rv, data = self.patch('/api/banks/{}'.format(b.id),
                              data={'cuit': '30500010312'})
        assert rv.status_code == 422
        assert data['messages']['cuit'] == ['CUIT field invalid.']
        assert b.cuit == '30500010912'


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

    def test_update_account_type(self):
        acc_type = BankAccountType(name='acc_type', abbr='AT')
        self.db.session.add(acc_type)
        self.db.session.commit()

        rv, data = self.get('/api/banks/account_types')
        assert rv.status_code == 200
        assert data['num_results'] == 1

        rv, data = self.patch('/api/banks/account_types/{}'.format(acc_type.id),
                              data={'abbr': 'at'})
        assert rv.status_code == 204

        assert acc_type.abbr == 'at'
