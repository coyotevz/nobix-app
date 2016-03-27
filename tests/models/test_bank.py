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
