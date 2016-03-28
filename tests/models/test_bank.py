# -*- coding: utf-8 -*-

from pytest import raises
from sqlalchemy.exc import IntegrityError

from tests import DBTestCase
from nbs.models.bank import Bank


class TestBank(DBTestCase):

    def test_raises_with_null_name(self):
        b = Bank()
        self.db.session.add(b)
        with raises(IntegrityError):
            self.db.session.commit()

    def test_raises_duplicated_name(self):
        b1 = Bank(name='b')
        b2 = Bank(name='b')
        self.db.session.add_all([b1, b2])
        with raises(IntegrityError):
            self.db.session.commit()
