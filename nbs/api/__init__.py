# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, url_for

#from nbs.api.user import user_api
from nbs.api.supplier import SupplierApi
from nbs.api.bank_account import bank_account_api

api = Blueprint('api', __name__, url_prefix='/api')


def configure_api(app):
    app.register_blueprint(api)
    #app.register_blueprint(user_api)
    SupplierApi.register(app)
    app.register_blueprint(bank_account_api)


@api.route('/')
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
