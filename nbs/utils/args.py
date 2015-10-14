# -*- coding: utf-8 -*-

from flask import request
from marshmallow import Schema, fields
from marshmallow.compat import text_type as _text_type
from webargs.flaskparser import FlaskParser, abort as _abort
import warnings

FIELD_MAPPING = {
    # type, [use_function] (preprocessing)
    fields.Integer: (int, None),
    fields.Number: (int, None),
    fields.Float: (float, None),
    fields.Decimal: (int, None),
    fields.String: (str, None),
    fields.Boolean: (bool, None),
    fields.UUID: (str, None),
    fields.DateTime: (str, None),
    fields.Date: (str, None),
    fields.Time: (str, None),
    fields.Email: (str, None),
    fields.URL: (str, None),

    fields.Field: (str, None),
    fields.Raw: (str, None),
}

def field2arg(field, allow_missing=False):
    type_, use = FIELD_MAPPING.get(type(field), (None, None))
    kwargs = {}

    if allow_missing:
        kwargs['allow_missing'] = True


    if isinstance(field, fields.Nested):
        type_ = build_args(field.schema)
        kwargs['multiple'] = field.many

    elif isinstance(field, fields.List):
        arg = field2arg(field.container)
        arg.multiple = True
        arg.allow_missing = allow_missing
        return arg

    return Arg(type_, **kwargs)

def build_args(cls_or_instance, allow_missing=False):
    """Return webargs declaration for a given marshmallow 
    :class:`Schema <marshmallow.Schema>`.
    """
    if isinstance(cls_or_instance, Schema):
        schema = cls_or_instance
        schema_cls = schema.__class__
    else:
        schema_cls = cls_or_instance
        schema = schema_cls()

    if getattr(schema_cls.Meta, 'fields', None) or\
       getattr(schema_cls.Meta, 'additional', None):
        warnings.warn('Only explicity-declared fields will be included in '
                      'webargs definition. Fields defined in Meta.fields or '
                      'Meta.additional are excluded')

    keys = set(schema.declared_fields.keys()) - set(schema.exclude)

    args = { fname: schema.declared_fields[fname] for fname in keys }

    return args


_parser = FlaskParser()

def get_args(args):
    return _parser.parse(args, request)
