# -*- coding: utf-8 -*-

from flask import Blueprint, url_for

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
    app.register_blueprint(bank_api)
