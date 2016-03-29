# -*- coding: utf-8 -*-

from flask import Blueprint, url_for

#from nbs.api.user import UserApi
#from nbs.api.supplier import SupplierApi
#from nbs.api.hr import EmployeeApi
#from nbs.api.bank_account import BankApi
#from nbs.api.purchase_order import PurchaseOrderApi
#from nbs.api.product import ProductApi

from nbs.api.supplier import supplier_api
from nbs.api.bank import bank_api

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('')
def index():
    return {
        'message': "This is api root.",
        'docs': url_for('api.documentation'),
    }

@api.route('/docs')
def documentation():
    return {'message': "Documentation"}

def configure_api(app):
    app.register_blueprint(api)
    app.register_blueprint(supplier_api)
    app.register_blueprint(bank_api)
    #UserApi.register(app)
    #SupplierApi.register(app)
    #EmployeeApi.register(app)
    #BankApi.register(app)
    #PurchaseOrderApi.register(app)
    #ProductApi.register(app)
