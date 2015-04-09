# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, '')

from flask import Flask, request, make_response, jsonify
from werkzeug.exceptions import default_exceptions, HTTPException

from nbs.models import configure_db
#from nbs.auth import configure_auth
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

    @app.route('/urls')
    def show_urls():
        column_headers = ('Rule', 'Endpoint', 'Methods')
        order = 'rule'
        rows = []
        rules = sorted(app.url_map.iter_rules(),
                       key=lambda rule: getattr(rule, order))
        for rule in rules:
            rows.append((rule.rule, rule.endpoint, ', '.join(rule.methods)))

        max_rule_length = max(len(r[0]) for r in rows)
        max_rule_length = max_rule_length if max_rule_length > 4 else 4

        max_ep_length = max(len(str(r[1])) for r in rows)
        max_ep_length = max_ep_length if max_ep_length > 8 else 8

        max_meth_length = max(len(str(r[2])) for r in rows)
        max_meth_length = max_meth_length if max_meth_length > 9 else 9

        str_template = '%-' + str(max_rule_length) + 's' + \
                       ' %-' + str(max_ep_length) + 's' + \
                       ' %-' + str(max_meth_length) + 's'
        table_width = max_rule_length + 2 + max_ep_length + 2 + max_meth_length

        out = str_template % column_headers
        out += '\n' + '-' * table_width
        for row in rows:
            out += '\n' + str_template % row
        out += '\n'

        return out

    def make_json_error(ex):
        err = {'error': str(ex)}
        if hasattr(ex, 'data'):
            err.update(**ex.data)
        return make_response(jsonify(err),
                             ex.code if isinstance(ex, HTTPException) else 500)

    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = make_json_error
