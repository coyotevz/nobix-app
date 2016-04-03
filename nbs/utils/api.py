# -*- coding: utf-8 -*-

import re
import copy
from math import ceil

from flask import request
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


def apply_query_filters(query):
    # TODO: Extract filter conditions from url querystring
    return query


def build_result(query, schema):

    if is_collection(query):
        query = apply_query_filters(query)

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

    return out
