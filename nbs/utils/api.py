# -*- coding: utf-8 -*-

import re
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
