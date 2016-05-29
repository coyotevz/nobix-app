# -*- coding: utf-8 -*-

from datetime import date
from dateutil.relativedelta import relativedelta

from nbs.models import db
from nbs.models.entity import Entity


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_record'

    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, unique=True)
    bkp_type = db.Column(db.Integer, nullable=False)
    type_code = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Record({}, {} {})>".format(self.user_code,
                                            self.datetime.isoformat(' '),
                                            "OUT" if self.type_code else "IN")


class Employee(Entity):
    __tablename__ = 'employee'
    __mapper_args__ = {'polymorphic_identity': 'employee'}

    employee_id = db.Column(db.Integer, db.ForeignKey('entity.id'),
                            primary_key=True)

    first_name = Entity._name_1
    last_name = Entity._name_2

    birth_date = db.Column(db.Date, nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    cuil = db.Column(db.Unicode, nullable=False)
    user_code = db.Column(db.Integer, unique=True)
    file_no = db.Column(db.Integer, unique=True)

    records = db.relationship(
        AttendanceRecord,
        primaryjoin=user_code == db.foreign(AttendanceRecord.user_code),
        backref='employee', lazy='dynamic', cascade='all, delete-orphan'
    )

    @property
    def age(self):
        today = date.today()
        return relativedelta(today, self.birth_date)

    @property
    def seniority(self):
        today = date.today()
        return relativedelta(today, self.hire_date)

    def month_records(self, year, month):
        return self.records\
            .filter(db.extract('year', AttendanceRecord.datetime) == year)\
            .filter(db.extract('month', AttendanceRecord.datetime) == month)

    def __repr__(self):
        return "<Employee '{}', age {}>".format(self.name, self.age.years)
