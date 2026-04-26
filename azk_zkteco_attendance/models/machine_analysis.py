# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields


class ZkMachineAttendance(models.Model):
    _name = "azk.machine.attendance"
    _description = "AZK Machine Attendance"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    device_id = fields.Char(string="Attendance ID")
    punch_type = fields.Selection([
        ("0", "Check In"), ("1", "Check Out"), ("2", "Break Out"),
        ("3", "Break In"), ("4", "Overtime In"), ("5", "Overtime Out"),
    ], string="Punching Type")
    attendance_type = fields.Selection([
        ("1", "Finger"), ("15", "Face"), ("2", "Type_2"),
        ("3", "Password"), ("4", "Card"),
    ], string="Category")
    punching_time = fields.Datetime(string="Punching Time")
    address_id = fields.Many2one("res.partner", string="Working Address")
    import_status = fields.Selection([
        ("imported", "Imported"), ("skipped", "Skipped"),
    ], string="Import Status")


class ReportZkDevice(models.Model):
    _name = "azk.report.daily.attendance"
    _description = "AZK Report Daily Attendance"
    _auto = False
    _order = "punching_day desc"

    name = fields.Many2one("hr.employee", string="Employee")
    punching_day = fields.Datetime(string="Date")
    address_id = fields.Many2one("res.partner", string="Working Address")
    attendance_type = fields.Selection([
        ("1", "Finger"), ("15", "Face"), ("2", "Type_2"),
        ("3", "Password"), ("4", "Card"),
    ], string="Category")
    punch_type = fields.Selection([
        ("0", "Check In"), ("1", "Check Out"), ("2", "Break Out"),
        ("3", "Break In"), ("4", "Overtime In"), ("5", "Overtime Out"),
    ], string="Punching Type")
    punching_time = fields.Datetime(string="Punching Time")
    import_status = fields.Selection([
        ("imported", "Imported"), ("skipped", "Skipped"),
    ], string="Import Status")

    def init(self):
        tools.drop_view_if_exists(self._cr, "azk_report_daily_attendance")
        self._cr.execute("""
            CREATE OR REPLACE VIEW azk_report_daily_attendance AS (
                SELECT min(z.id) AS id, z.employee_id AS name, z.write_date AS punching_day,
                    z.address_id, z.attendance_type, z.punching_time, z.punch_type, z.import_status
                FROM azk_machine_attendance z JOIN hr_employee e ON (z.employee_id = e.id)
                GROUP BY z.employee_id, z.write_date, z.address_id,
                    z.attendance_type, z.punch_type, z.punching_time, z.import_status
            )
        """)
