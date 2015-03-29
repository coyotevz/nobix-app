# -*- coding: utf-8 -*-

from werkzeug.routing import BaseConverter


class ListConverter(BaseConverter):

    _subtypes = {
        'int': int,
        'str': str,
        'u': unicode,
    }

    def __init__(self, url_map, subtype=None, mutable=False):
        super(ListConverter, self).__init__(url_map)
        self.subtype = subtype
        self.mutable = mutable
        if subtype:
            rearg = {'int': '\d', 'str': '\w', 'u': '\w'}[subtype]
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
