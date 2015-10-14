# -*- coding: utf-8 -*-

from flask import jsonify, url_for, abort
from sqlalchemy.exc import IntegrityError
from webargs import ValidationError
from nbs.models import db, Bank, BankAccount
from nbs.schema import BankAccountSchema, BankSchema
from nbs.utils.api import ResourceApi, route, build_result
from nbs.utils.args import fields, get_args, build_args

ba_schema = BankAccountSchema()
post_ba_schema = BankAccountSchema(exclude=('bank','supplier_name'))
bank_schema = BankSchema()

class BankAccountApi(ResourceApi):
    route_base = 'bank_accounts'

    post_args = build_args(post_ba_schema, allow_missing=True)

    def index(self):
        """
        Returns a paginated list of bank accounts registered in the system
        """
        q = BankAccount.query
        if self.obj:
            q = q.filter(BankAccount.supplier==self.obj)
        return build_result(q, ba_schema)

    @route('<int:id>')
    def get(self, id):
        account = BankAccount.query.get_or_404(id)
        if self.obj:
            if not account.supplier == self.obj:
                abort(404)
        return build_result(account, ba_schema)

    def post(self):
        args = get_args(self.post_args)
        if self.obj:
            args['supplier_id'] = self.obj.id
        data, errors = post_ba_schema.load(args)
        ba = BankAccount(**data)
        db.session.add(ba)
        db.session.commit()
        return '', 201, {'Location': url_for('.get', pk=self.obj.id, id=ba.id,
                                             _external=True)}

    @route('<int:id>', methods=['DELETE'])
    def delete(self, id):
        account = BankAccount.query.get_or_404(id)
        if self.obj:
            if not account.supplier == self.obj:
                abort(404)
        db.session.delete(account)
        db.session.commit()
        return '', 204


def unique_bank_name(val):
    exists = Bank.query.filter(Bank.name==val).first()
    if exists is not None:
        raise ValidationError('Bank name must be unique', status_code=409)

class BankApi(ResourceApi):
    route_base = 'banks'

    bank_post = {
        'name': fields.String(required=True, validate=unique_bank_name),
    }

    def index(self):
        q = Bank.query.order_by(Bank.name)
        return build_result(q, bank_schema)

    @route('<int:id>', methods=['PUT'])
    def put(self, id):
        b = Bank.query.get_or_404(id)
        args = get_args(self.bank_post)
        b.name = args['name']
        db.session.commit()
        return '', 204

    def post(self):
        args = get_args(self.bank_post)
        b = Bank(name=args['name'])
        db.session.add(b)
        db.session.commit()
        # Only return id of created Bank, we don't have individual retrieves
        return jsonify({'id': b.id}), 201

    @route('<int:id>', methods=['DELETE'])
    def delete(self, id):
        b = Bank.query.get_or_404(id)
        db.session.delete(b)
        try:
            db.session.commit()
        except IntegrityError:
            abort(409, description='Unable to delete bank')
        return '', 204

    def account_types(self):
        return jsonify(**BankAccount._account_type)
