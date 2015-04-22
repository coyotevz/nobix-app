# -*- coding: utf-8 -*-

from flask import jsonify, request, url_for
from nbs.models import db, Employee, AttendanceRecord
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

    @route('<int:id>')
    def get(self, id):
        employee = self.get_obj(id)
        return build_result(employee, employee_s)

    @route('<int:id>', methods=['DELETE'])
    def delete(self, id):
        employee = self.get_obj(id)
        db.session.delete(employee)
        db.session.commit()
        # TODO: Remove related attendance records
        return '', 204
