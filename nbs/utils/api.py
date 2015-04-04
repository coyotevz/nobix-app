# -*- coding: utf-8 -*-

from flask.ext.classy import FlaskView, route


class ResourceApi(FlaskView):
    trailing_slash = False
    endpoint_prefix = 'api'
    route_prefix = '/api'

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
        if cls.__name__.endswith("Api"):
            return cls.__name__[:-3].lower()
        else:
            return cls.__name__.lower()
