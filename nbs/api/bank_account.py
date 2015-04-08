# -*- coding: utf-8 -*-

from flask import jsonify
from nbs.models import db, Bank, BankAccount
from nbs.schema import BankAccountSchema
from nbs.utils.api import ResourceApi, route
from nbs.utils.args import Arg, get_args

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

    def banks(self):
        return jsonify(objects=[{'id': b.id, 'name': b.name}
                                for b in Bank.query.order_by(Bank.name)])


bank_post = {
    'name': Arg(str),
}

class BankApi(ResourceApi):
    route_base = 'banks'

    def index(self):
        return '', 200
        return jsonify(objects=[{'id': b.id, 'name': b.name}
                                for b in Bank.query.order_by(Bank.name)])

    def post(self):
        args = get_args(bank_post)
        b = Bank(name=args['name'])
        db.session.add(b)
        db.session.commit()
        return jsonify({'id': b.id}), 201

    def delete(self, id):
        b = Bank.query.get_or_404(int(id))
        db.session.delete(b)
        db.session.commit()
        return jsonify()
