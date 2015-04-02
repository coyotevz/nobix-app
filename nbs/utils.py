# -*- coding: utf-8 -*-

from werkzeug.routing import BaseConverter
from marshmallow import Schema, fields
from webargs import Arg
import warnings


class ListConverter(BaseConverter):

    _subtypes = {
        'int': int,
        'str': str,
    }

    def __init__(self, url_map, subtype=None, mutable=False):
        super(ListConverter, self).__init__(url_map)
        self.subtype = subtype
        self.mutable = mutable
        if subtype:
            rearg = {'int': '\d', 'str': '\w'}[subtype]
        else:
            rearg = '[\d\w]'
        self.regex = '{0}+(?:,{0}*)+'.format(rearg)

    def to_python(self, value):
        retval = filter(None, value.split(','))
        if self.subtype in self._subtypes:
            retval = map(self._subtypes[self.subtype], retval)
        if not self.mutalbe:
            retval = tuple(retval)
        return retval

    def to_url(self, value):
        return ','.join(BaseConverter.to_url(value) for value in values)


class RangeConverter(BaseConverter):

    regex = '\d+-\d+'

    def to_python(self, value):
        s, e = value.split('-')
        return list(range(int(s), int(e)+1))

    def to_url(self, value):
        return '-'.join([value[0], value[-1]])


class RangeListConverter(BaseConverter):

    regex = '(?:\d+|\d+-\d+)+(?:,(?:\d+|\d+-\d+))*'

    def to_python(self, value):
        retval = []
        for gr in value.split(','):
            if '-' in gr:
                s, e = gr.split('-')
                retval.extend(list(range(int(s), int(e)+1)))
            else:
                retval.append(int(gr))
        return retval

    def to_url(self, values):
        t = -1
        s = []
        segs = []
        for v in sorted(values):
            if t+1 == v:
                s.append(v)
            else:
                segs.append(s)
                s = [v]
            t = v
        outs = []
        for r in sorted(segs):
            if len(r) > 1:
                r = sorted(r)
                outs.append('{}-{}'.format(r[0],r[-1]))
            else:
                outs.append('{}'.format(r[0]))
        return ','.join(BaseConverter.to_url(out) for out in outs)



#### Test code
FIELD_MAPPING = {
    # type, [use_function] (preprocessing)
    fields.Integer: (int, None),
    fields.Number: (int, None),
    fields.Float: (float, None),
    fields.Fixed: (float, None),
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

def field2arg(field):
    type_, use = FIELD_MAPPING.get(type(field), (None, None))
    kwargs = {}

    if isinstance(field, fields.Nested):
        type_ = marshmallow2webargs(field.schema)
        kwargs['multiple'] = field.many

    elif isinstance(field, fields.List):
        arg = field2arg(field.container)
        arg.multiple = True
        return arg

    return Arg(type_, **kwargs)

def marshmallow2webargs(cls_or_instance):
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

    args = { field_name: field2arg(schema.declared_fields[field_name]) for\
             field_name in keys }

    return args
