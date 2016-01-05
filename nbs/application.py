# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, '')

from flask import Flask, request, make_response, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException
from webargs.flaskparser import abort

from nbs.models import configure_db
# from nbs.auth import configure_auth
from nbs.api import configure_api
from nbs.utils.converters import (
    ListConverter, RangeConverter, RangeListConverter
)


DEFAULT_APPNAME = 'nobix-app-server'


def create_app(config=None, app_name=None):

    if app_name is None:
        app_name = DEFAULT_APPNAME

    app = Flask(app_name, static_folder=None)

    configure_app(app, config)
    configure_db(app)
    # configure_auth(app)
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
        request.select = set(
            ','.join(request.args.getlist('select')).split(',')
        )
        request.omit = set(
            ','.join(request.args.getlist('omit')).split(',')
        )
        try:
            request.page = int(request.args.get('page', 1))
            request.per_page = min(int(request.args.get('per_page', 25)),
                                   max_per_page)
        except ValueError:
            abort(400, message='Invalid parameter type')

    @app.after_request
    def add_cors_headers(response):
        if 'Origin' in request.headers:

            a = response.headers.add
            a('Access-Control-Allow-Origin', request.headers['Origin'])
            a('Access-Control-Allow-Credentials', 'true')
            a('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            a('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    @app.route('/urls')
    def show_urls():
        column_headers = ('Rule', 'Endpoint', 'Methods')
        order = 'rule'
        rows = [('-'*4, '-'*8, '-'*9)]  # minimal values to take
        rules = sorted(app.url_map.iter_rules(),
                       key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, ', '.join(rule.methods)))

        rule_l = len(max(rows, key=lambda r: len(r[0]))[0])
        ep_l = len(max(rows, key=lambda r: len(r[1]))[1])
        meth_l = len(max(rows, key=lambda r: len(r[2]))[2])

        str_template = '%-' + str(rule_l) + 's' + \
                       ' %-' + str(ep_l) + 's' + \
                       ' %-' + str(meth_l) + 's'
        table_width = rule_l + 2 + ep_l + 2 + meth_l

        out = (str_template % column_headers) + '\n' + '-' * table_width
        for row in rows[1:]:
            out += '\n' + str_template % row

        return out + '\n'

    def make_json_error(ex):
        err = {'error': str(ex)}
        if hasattr(ex, 'data') and 'messages' in ex.data:
            err.update({'messages': ex.data['messages']})
        return make_response(jsonify(err),
                             ex.code if isinstance(ex, HTTPException) else 500)

    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = make_json_error
