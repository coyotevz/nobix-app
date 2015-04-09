# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, url_for

#from nbs.api.user import UserApi
from nbs.api.supplier import SupplierApi
from nbs.api.bank_account import BankAccountApi, BankApi

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('')
def index():
    return jsonify({
        'message': "This is api root.",
        'docs': url_for('api.documentation'),
    })

@api.route('/docs')
def documentation():
    return jsonify({
        'message': "Documentation",
    })

def configure_api(app):
    app.register_blueprint(api)
    #UserApi.register(app)
    SupplierApi.register(app)
    BankAccountApi.register(app)
    BankApi.register(app)
