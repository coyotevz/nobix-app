# -*- coding: utf-8 -*-

from flask import jsonify, request, url_for
from nbs.models import db, Employee, AttendanceRecord
from nbs.schema import EmployeeSchema, AttendanceRecordSchema
from nbs.utils.api import ResourceApi, NestedApi, route, build_result
from nbs.utils.args import get_args, build_args, Arg, ValidationError

employee_s = EmployeeSchema()
writable_schema = EmployeeSchema(
    exclude=('id', 'modified', 'created')
)

ar_schema = AttendanceRecordSchema()

def unique_file_no(val):
    exists = Employee.query.filter(Employee.file_no==val).first()
    if exists is not None:
        raise ValidationError('Employee file_no must be unique',
                              status_code=409)

def unique_user_code(val):
    exists = Employee.query.filter(Employee.user_code==val).first()
    if exists is not None:
        raise ValidationError('Employee user_code must be unique',
                              status_code=409)

post_args = build_args(writable_schema, allow_missing=True)
post_args['file_no'] = Arg(int, required=True, validate=unique_file_no)
post_args['user_code'] = Arg(int, required=True, validate=unique_user_code)

patch_args = build_args(writable_schema, allow_missing=True)
patch_args['file_no'] = Arg(int, validate=unique_file_no, allow_missing=True)
patch_args['user_code'] = Arg(int, validate=unique_user_code,
                              allow_missing=True)

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

    @route('<int:id>', methods=['PATCH'])
    def patch(self, id):
        employee = self.get_obj(id)
        args = get_args(patch_args)
        for k, v in args.items():
            setattr(employee, k, v)
        db.session.commit()
        return '', 204

    def post(self):
        args = get_args(post_args)
        employee, e = writable_schema.load(args)
        db.session.add(employee)
        db.session.commit()
        return '', 201, {'Location': url_for('.get', id=employee.id,
                                             _external=True)}

    @route('<int:id>', methods=['DELETE'])
    def delete(self, id):
        employee = self.get_obj(id)
        db.session.delete(employee)
        db.session.commit()
        return '', 204

    @route('<int:id>/records/<int:year>/<int:month>')
    def get_records(self, id, year, month):
        employee = self.get_obj(id)
        records = employee.month_records(year, month)
        return build_result(records, ar_schema)
