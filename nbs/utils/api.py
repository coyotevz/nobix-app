# -*- coding: utf-8 -*-

import re
import inspect
import copy
from math import ceil

from flask import request, jsonify
from flask.ext.classy import FlaskView, route
from marshmallow.utils import is_collection

class Pagination(object):

    def __init__(self, iterable, page, per_page):
        iterable = list(iterable)
        self.total = len(iterable)
        offset = (page-1) * per_page
        limit = min(offset+per_page, self.total)
        self.items = iterable[offset:limit]
        self.page = page
        self.per_page = per_page

    @property
    def pages(self):
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages


def uncamel(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ResourceApi(FlaskView):
    trailing_slash = False
    endpoint_prefix = 'api'
    route_prefix = '/api'
    name_suffix = 'Api'
    obj = None

    @classmethod
    def build_route_name(cls, method_name):
        parts = []
        if hasattr(cls, 'endpoint_prefix') and cls.endpoint_prefix is not None:
            parts.append(cls.endpoint_prefix)
        parts.append(cls.get_basic_name())
        if method_name:
            parts.append(method_name)
        return '.'.join(parts)

    @classmethod
    def get_basic_name(cls):
        return uncamel(re.sub('(.)({})'.format(cls.name_suffix),
                              r'\1', cls.__name__))

    @classmethod
    def register(cls, app, route_base=None, subdomain=None, route_prefix=None,
                 trailing_slash=None):
        super(ResourceApi, cls).register(app, route_base=route_base,
                           subdomain=subdomain, route_prefix=route_prefix,
                           trailing_slash=trailing_slash)

        isnested = lambda o: isinstance(o, NestedApi)

        members = inspect.getmembers(cls, predicate=isnested)
        for name, value in members:
            nested_cls = value.nested_cls
            value.register(name, app, cls)


class NestedApi(object):

    def __init__(self, nested_cls, pk_name='pk', pk_converter='any',
                 getter='get_obj'):
        self.nested_cls = nested_cls
        self.pk_name = pk_name
        self.pk_converter = pk_converter
        self.getter = getter

    def register(self, attr_name, app, parent):
        """
        This is a lazy implementation to register nested api, by the moment
        this fits well for this project.
        """
        prefix_parts = []
        class cls(self.nested_cls):
            pass
        cls.__name__ = self.nested_cls.__name__

        getter = parent.__dict__.get(self.getter, None)
        if not getter or not isinstance(getter, classmethod):
            raise ValueError("Parent class ({}) must define '{}' as "
                    "classmethod".format(parent.__name__, self.getter))

        if parent.route_prefix:
            prefix_parts.append(parent.route_prefix)
        if parent.get_route_base():
            prefix_parts.append(parent.get_route_base())

        route_parts = [
            '<{}:{}>'.format(self.pk_converter, self.pk_name),
            attr_name,
        ]

        # change endpoint prefix for registration
        cls.endpoint_prefix = parent.build_route_name(None)

        cls.register(app, route_prefix='/'.join(prefix_parts),
                     route_base='/'.join(route_parts))

        def before_request(nested, name, **kwargs):
            pk = request.view_args.pop(self.pk_name, None)
            nested.obj = getattr(parent, self.getter)(pk)
            if hasattr(nested, 'orig_before_request'):
                return nested.orig_before_request(name, **request.view_args)

        if hasattr(cls, 'before_request'):
            cls.orig_before_request = cls.before_request
        cls.before_request = before_request
        cls.parent = parent


def build_result(query, schema):

    if is_collection(query):
        if hasattr(query, 'paginate') and callable(query.paginate):
            result = query.paginate(request.page, request.per_page)
        else:
            result = Pagination(query, request.page, request.per_page)

        out = {
            'num_results': result.total,
            'page': result.page,
            'num_pages': result.pages,
        }
        items = result.items

    else:
        items = query

    if request.select or request.omit:
        schema = copy.copy(schema)
        if list(request.select)[0]:
            schema.only = request.select.intersection(schema.fields.keys())
        if list(request.omit)[0]:
            only_set = set(schema.only or schema.fields.keys())
            schema.only = only_set.difference(request.omit)

        if schema.only:
            schema.only.add('id')

    if is_collection(items):
        out['objects'] = schema.dump(items, many=True).data
    else:
        out = schema.dump(items, many=False).data

    return jsonify(out)
