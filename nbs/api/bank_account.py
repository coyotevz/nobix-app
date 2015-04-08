# -*- coding: utf-8 -*-

from flask import jsonify, url_for
from nbs.models import db, Bank, BankAccount
from nbs.schema import BankAccountSchema
from nbs.utils.api import ResourceApi, route
from nbs.utils.args import Arg, get_args, build_args, ValidationError

ba_schema = BankAccountSchema()
post_args = build_args(ba_schema)

class BankAccountApi(ResourceApi):
    route_base = 'bank_accounts'

    def index(self):
        """
        Returns a paginated list of bank accounts registered in the system
        """
        q = BankAccount.query
        return jsonify(objects=ba_schema.dump(q, many=True).data)

    def get(self, id):
        account = BankAccount.query.get_or_404(int(id))
        return jsonify(ba_schema.dump(account).data)

    def post(self):
        args = get_args(post_args)
        return jsonify(args)

    def delete(self, id):
        account = BankAccount.query.get_or_404(int(id))
        db.session.delete(b)
        db.session.commit()
        return '', 204


def unique_bank_name(val):
    exists = Bank.query.filter(Bank.name==val).first()
    if exists is not None:
        raise ValidationError('Bank name must be unique', status_code=409)

bank_post = {
    'name': Arg(str, required=True, validate=unique_bank_name),
}

class BankApi(ResourceApi):
    route_base = 'banks'

    def index(self):
        return jsonify(objects=[{'id': b.id, 'name': b.name}
                                for b in Bank.query.order_by(Bank.name)])

    def post(self):
        args = get_args(bank_post)
        b = Bank(name=args['name'])
        db.session.add(b)
        db.session.commit()
        # Only return id of created Bank, we don't have individual retrieves
        return jsonify({'id': b.id}), 201

    def delete(self, id):
        b = Bank.query.get_or_404(int(id))
        db.session.delete(b)
        db.session.commit()
        return '', 204
