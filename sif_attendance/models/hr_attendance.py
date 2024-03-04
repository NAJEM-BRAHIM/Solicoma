# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                if not attendance.employee_id.night_hours:
                    delta = attendance.check_out - attendance.check_in
                    hours = delta.total_seconds() / 3600.0
                    total_hours = (hours - 1)
                    attendance.worked_hours = total_hours
                else:
                    super(HrAttendance, self)._compute_worked_hours()
            else:
                attendance.worked_hours = False


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    night_hours = fields.Boolean(string="Night hours")
