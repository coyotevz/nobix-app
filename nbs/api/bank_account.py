# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from nbs.models import BankAccount
from nbs.schema import BankAccountSchema

bank_account_api = Blueprint('api.bank_account', __name__, url_prefix='/api/bank_accounts')
bank_account_schema = BankAccountSchema()
bank_accounts_schema = BankAccountSchema(many=True)


@bank_account_api.route('', methods=['GET'])
def list():
    """
    Returns a paginated list of bank accounts registered in the system.
    """
    return jsonify(objects=bank_accounts_schema.dump(BankAccount.query).data)

@bank_account_api.route('/<int:id>', methods=['GET'])
def get(id):
    account = BankAccount.query.get_or_404(id)
    return jsonify(bank_account_schema.dump(account).data)
