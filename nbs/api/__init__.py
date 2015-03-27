# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, url_for

#from nbs.api.user import user_api
from nbs.api.supplier import supplier_api

api = Blueprint('api', __name__, url_prefix='/api')


def configure_api(app):
    app.register_blueprint(api)
    #app.register_blueprint(user_api)
    app.register_blueprint(supplier_api)


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
