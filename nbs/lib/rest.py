# -*- coding: utf-8 -*-

"""
    nbs.lib.rest
    ~~~~~~~~~~~~

    Provides tools for building REST interfaces.
    primary function built_result().
    
    Limitations:
    - Only work for simple queries agains one model.

    Depends on:
    - SQLAlchemy
    - Flask
    - Marshmallow
"""

import copy
from math import ceil
from collections import namedtuple

from sqlalchemy import and_
from sqlalchemy.orm import (
    ColumnProperty, SynonymProperty, RelationshipProperty, object_mapper
)
from sqlalchemy.orm.util import class_mapper
from flask import request, current_app
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


OPERATORS = {

    # General comparators
    'eq': lambda f, a: f == a,
    'neq': lambda f, a: f != a,
    'gt': lambda f, a: f > a,
    'gte': lambda f, a: f >= a,
    'lt': lambda f, a: f < a,
    'lte': lambda f, a: f <= a,

    # String operators
    'contains': lambda f, a: f.contains(a),
    'icontains': lambda f, a: f.ilike('%'+a+'%'),
    'endswith': lambda f, a: f.endswith(a),
    'startswith': lambda f, a: f.startswith(a),

    # List operators
    'in': lambda f, a: f.in_(a),
    'nin': lambda f, a: ~f.in_(a),

}

SORT_ORDER = {
    # Sort order
    'asc': lambda f: f.asc,
    'desc': lambda f: f.desc,
}

_default_filter = 'eq'

#: Represents and "order by" in SQL query expression
OrderBy = namedtuple('OrderBy', 'field direction')

#: Represents a filter to apply to a SQL query
Filter = namedtuple('Filter', 'field operator argument')


def parse_filters(filters):
    retval = []
    for f in filters:
        field, op, arg = (f.split(':') + [None, None])[:3]
        if op is None:
            # Malformed filter ignore
            continue
        if arg is None:
            if op in OPERATORS:
                # Argument missing ignore
                continue
            # Default operator 'eq'
            arg = op
            op = _default_filter
        retval.append(Filter(field, op, arg))
    return retval


def create_operation(model, fieldname, operator, argument, relation=None):
    """
    Translate an operation described as string to a valida SQLAlchemy query
    parameter using a field or relation of the model.
    """
    opfunc = OPERATORS.get(operator)
    field = getattr(model, relation or fieldname, None)
    if opfunc and field:
        return opfunc(field, argument)


def create_filters(filters, model):
    "Returns a list of operations on `model`specified in the `filters` list."
    retfilters = []
    for f in filters:
        fname = f.field
        relation = None
        if '.' in fname:
            relation, fname = fname.split('.')
        arg = create_operation(model, fname, f.operator, f.argument, relation)
        retfilters.append(arg)
    return list(filter(lambda x: x is not None, retfilters))


def apply_query_filters(query, model=None):
    filters = request.args.getlist('filter')
    if filters:
        filters = parse_filters(filters)
        if model is None:
            # Retreive model from query, FIXME: only first model retrieved
            model = query.column_descriptions[0]['type']
        filters = create_filters(filters, model)
        query = query.filter(and_(*filters))
    return query


def select_and_omit(schema):
    "Fills schema.only based on 'select' and 'omit' query string parameters"
    select = set(','.join(request.args.getlist('select')).split(','))
    omit = set(','.join(request.args.getlist('omit')).split(','))
    if select or omit:
        schema = copy.copy(schema)
        if list(select)[0]:
            schema.only = select.intersection(schema.fields.keys())
        if list(omit)[0]:
            only_set = set(schema.only or schema.fields.keys())
            schema.only = only_set.difference(omit)
        if schema.only:
            # Always return id field
            schema.only.add('id')
    return schema

def paginate(query):
    max_per_page = current_app.config.get('MAX_ITEMS_PER_PAGE', 100)
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 25)),
                       max_per_page)
    except ValueError:
        from flask import abort
        abort(400, message='Invalid parameter type')

    if hasattr(query, 'paginate') and callable(query.paginate):
        return query.paginate(page, per_page)
    else:
        return Pagination(query, page, per_page)


def build_result(query, schema, model=None):
    schema = select_and_omit(schema)

    if is_collection(query):
        query = apply_query_filters(query, model)
        result = paginate(query)

        return {
            'num_results': result.total,
            'page': result.page,
            'num_pages': result.pages,
            'objects': schema.dump(result.items, many=True).data,
        }

    else:
        return schema.dump(query, many=False).data
