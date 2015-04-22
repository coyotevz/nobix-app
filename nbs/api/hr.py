# -*- coding: utf-8 -*-

from flask import jsonify, request, url_for
from nbs.models import Employee, AttendanceRecord
from nbs.schema import EmployeeSchema, AttendanceRecordSchema
from nbs.utils.api import ResourceApi, NestedApi, route, build_result
from nbs.utils.args import get_args, build_args

employee_s = EmployeeSchema()


class EmployeeApi(ResourceApi):
    route_base = 'employees'

    @classmethod
    def get_obj(cls, id):
        return Employee.query.get_or_404(id)

    def index(self):
        return build_result(Employee.query, employee_s)
