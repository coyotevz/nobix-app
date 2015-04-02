# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, '')

from flask import Flask, request, make_response, jsonify

from nbs.models import configure_db
#from nbs.auth import configure_auth
from nbs.api import configure_api
from nbs.utils import ListConverter, RangeConverter, RangeListConverter


DEFAULT_APPNAME = 'nobix-app-server'


def create_app(config=None, app_name=None):

    if app_name is None:
        app_name = DEFAULT_APPNAME

    app = Flask(app_name, static_folder=None)

    configure_app(app, config)
    configure_db(app)
    #configure_auth(app)
    configure_api(app)

    return app


def configure_app(app, config=None):

    if config is not None:
        app.config.from_object(config)
    else:
        try:
            app.config.from_object('localconfig.LocalConfig')
        except ImportError:
            app.config.from_object('nbs.config.DevelopmentConfig')


    # Add additional converters
    app.url_map.converters['list'] = ListConverter
    app.url_map.converters['range'] = RangeConverter
    app.url_map.converters['rangelist'] = RangeListConverter

    @app.before_request
    def set_page_params():
        max_per_page = app.config.get('MAX_ITEMS_PER_PAGE', 100)
        request.page = int(request.args.get('page', 1))
        request.per_page = min(int(request.args.get('per_page', 25)),
                               max_per_page)

    @app.errorhandler(400)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 400)

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)
