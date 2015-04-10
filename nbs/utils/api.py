# -*- coding: utf-8 -*-

import re
import inspect
from flask.ext.classy import FlaskView, route


def uncamel(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class ResourceApi(FlaskView):
    trailing_slash = False
    endpoint_prefix = 'api'
    route_prefix = '/api'
    name_suffix = 'Api'

    @classmethod
    def build_route_name(cls, method_name):
        parts = []
        if hasattr(cls, 'endpoint_prefix') and cls.endpoint_prefix is not None:
            parts.append(cls.endpoint_prefix)
        parts.append(cls.get_basic_name())
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

    def __init__(self, nested_cls, subpath=None):
        self.nested_cls = nested_cls
        self.subpath = subpath

    def register(self, attr_name, app, parent):
        prefix_parts = []
        route_parts = []
        if parent.route_prefix:
            prefix_parts.append(parent.route_prefix)
        if parent.get_route_base():
            prefix_parts.append(parent.get_route_base())
        if self.subpath:
            route_parts.append(self.subpath)
        route_parts.append(attr_name)
        self.nested_cls.register(app, route_prefix='/'.join(prefix_parts),
                                 route_base='/'.join(route_parts))
