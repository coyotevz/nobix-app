# -*- coding: utf-8 -*-

from webargs import Arg
from marshmallow import Schema, fields
from nbs.utils import build_args

def test_integer_field():
    class TestSchema(Schema):
        integer = fields.Integer()

    test_args = {
        'integer': Arg(int),
    }

    assert test_args == build_args(TestSchema())
