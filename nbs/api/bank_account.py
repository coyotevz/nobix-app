# -*- coding: utf-8 -*-

from flask import jsonify
from nbs.models import BankAccount
from nbs.schema import BankAccountSchema
from nbs.utils.api import ResourceApi, route

ba_schema = BankAccountSchema()


class BankAccountApi(ResourceApi):
    route_base = 'bank_accounts'

    def index(self):
        """
        Returns a paginated list of bank accounts registered in the system
        """
        q = BankAccount.query
        return jsonify(objects=ba_schema.dump(q, many=True).data)

    @route('/<int:id>')
    def get(self, id):
        account = BankAccount.query.get_or_404(id)
        return jsonify(ba_schema.dump(account).data)
