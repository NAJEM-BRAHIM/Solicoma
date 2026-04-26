# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta
import logging
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import pytz
import time as aztime
from zk import ZK

log = logging.getLogger(__name__)


class ZkMachine(models.Model):
    _name = 'azk.machine'
    _description = 'AZK Machine'

    name = fields.Char(string='Machine', required=True)
    machine_ip = fields.Char("Machine IP/DNS", required=True)
    password = fields.Char('Password', help="Password must be digits.")
    port_num = fields.Integer(string='Port No', required=True)
    serial_num = fields.Char("Serial num", readonly=True)
    timeout = fields.Integer("Connection Timeout", default=10)
    auto_create_employee = fields.Boolean("Auto create employee", default=False)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    last_run_status = fields.Boolean('Machine OK', default=False)
    last_error_msg = fields.Char("Last Error")

    @api.onchange('password')
    def _onchange_password(self):
        if self.password:
            try:
                int(self.password)
            except ValueError:
                raise UserError(_('Password must be digits.'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.password:
                try:
                    int(rec.password)
                except ValueError:
                    raise UserError(_('Password must be digits.'))
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'password' in vals:
            for rec in self:
                if rec.password:
                    try:
                        int(rec.password)
                    except ValueError:
                        raise UserError(_('Password must be digits.'))
        return res

    def check_user_id_availabilty(self, user_id, conn=False):
        if not conn:
            conn, _ = self.connect()
        machine_users = conn.get_users()
        for user in machine_users:
            if user.user_id == user_id:
                return user
        return False

    def check_username_exists(self, name, conn=False):
        if not conn:
            conn, _ = self.connect()
        machine_users = conn.get_users()
        for user in machine_users:
            if user.name.lower() == name.lower():
                return user
        return False

    def test_connection(self):
        conn, _ = self.connect()
        if conn:
            conn.disconnect()
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'Connection status', 'message': 'SUCCESS', 'sticky': False, 'type': 'success'}}
        return {'type'
cat > /home/odoo/src/user/azk_zkteco_attendance/models/zk_machine.py << 'PYEOF'
# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta
import logging
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import pytz
import time as aztime
from zk import ZK

log = logging.getLogger(__name__)


class ZkMachine(models.Model):
    _name = 'azk.machine'
    _description = 'AZK Machine'

    name = fields.Char(string='Machine', required=True)
    machine_ip = fields.Char("Machine IP/DNS", required=True)
    password = fields.Char('Password', help="Password must be digits.")
    port_num = fields.Integer(string='Port No', required=True)
    serial_num = fields.Char("Serial num", readonly=True)
    timeout = fields.Integer("Connection Timeout", default=10)
    auto_create_employee = fields.Boolean("Auto create employee", default=False)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    last_run_status = fields.Boolean('Machine OK', default=False)
    last_error_msg = fields.Char("Last Error")

    @api.onchange('password')
    def _onchange_password(self):
        if self.password:
            try:
                int(self.password)
            except ValueError:
                raise UserError(_('Password must be digits.'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.password:
                try:
                    int(rec.password)
                except ValueError:
                    raise UserError(_('Password must be digits.'))
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'password' in vals:
            for rec in self:
                if rec.password:
                    try:
                        int(rec.password)
                    except ValueError:
                        raise UserError(_('Password must be digits.'))
        return res

    def check_user_id_availabilty(self, user_id, conn=False):
        if not conn:
            conn, _ = self.connect()
        machine_users = conn.get_users()
        for user in machine_users:
            if user.user_id == user_id:
                return user
        return False

    def check_username_exists(self, name, conn=False):
        if not conn:
            conn, _ = self.connect()
        machine_users = conn.get_users()
        for user in machine_users:
            if user.name.lower() == name.lower():
                return user
        return False

    def test_connection(self):
        conn, _ = self.connect()
        if conn:
            conn.disconnect()
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'Connection status', 'message': 'SUCCESS', 'sticky': False, 'type': 'success'}}
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': 'Connection status', 'message': 'Failed: %s' % self.last_error_msg, 'sticky': False, 'type': 'danger'}}

    def connect(self):
        zk, conn = None, None
        try:
            zk = ZK(self.machine_ip, port=self.port_num, password=self.password, timeout=self.timeout, ommit_ping=True)
            conn = zk.connect()
            self.last_run_status = True
            self.last_error_msg = None
            self.serial_num = conn.get_serialnumber()
        except Exception as ex:
            log.error("Failed to connect to: %s[%s:%s]", self.name, self.machine_ip, self.port_num, exc_info=True)
            self.last_run_status = False
            self.last_error_msg = str(ex)
        return conn, zk

    def clear_attendance(self):
        conn = None
        try:
            conn, _ = self.connect()
            if conn:
                conn.clear_attendance()
        except Exception:
            log.error("Failed to clear attendance for machine: %s", self.name, exc_info=True)
        finally:
            if conn:
                conn.disconnect()

    @api.model
    def cron_download(self):
        for machine in self.env['azk.machine'].search([]):
            try:
                machine.download_attendance()
            except Exception:
                log.error("Failed to download attendance for %s", machine.name, exc_info=True)

    def download_attendance(self):
        log.info("Downloading attendance for '%s'", self.name)
        AZKAttendance = self.env['azk.machine.attendance']
        HRAttendance = self.env['hr.attendance']
        local_tz = pytz.timezone(self.env.user.tz or self.env.user.partner_id.tz or 'GMT')
        conn = None
        checkins = checkouts = 0
        before = aztime.time()
        try:
            conn, _ = self.connect()
            if not conn:
                return
            lst_attendance = conn.get_attendance()
            machine_users = conn.get_users()
            users_by_id = {u.user_id: u for u in machine_users}
            employees_by_device_id = {
                e.device_id: e for e in self.env['hr.employee'].search(
                    [('device_id', 'in', [u.user_id for u in machine_users])])}
            today = datetime.today().date()
            lst_attendance = [a for a in lst_attendance if a.timestamp.date() <= today]
            latest = AZKAttendance.search([], order="punching_time desc", limit=1)
            if latest:
                cutoff = latest.punching_time - timedelta(days=3)
                lst_attendance = [a for a in lst_attendance if a.timestamp > cutoff]
            emp_cache = {}
            for a_rec in sorted(lst_attendance, key=lambda a: a.timestamp):
                try:
                    emp_device_id = str(a_rec.user_id)
                    try:
                        local_dt = local_tz.localize(a_rec.timestamp, is_dst=None)
                    except pytz.exceptions.AmbiguousTimeError:
                        local_dt = local_tz.localize(a_rec.timestamp, is_dst=True)
                    utc_str = local_dt.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
                    atten_time_ts = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S")
                    atten_time = fields.Datetime.to_string(atten_time_ts)
                    employee = employees_by_device_id.get(emp_device_id)
                    if not employee:
                        employee = self.find_or_create_employee(users_by_id[emp_device_id]) if emp_device_id in users_by_id else False
                        employees_by_device_id[emp_device_id] = employee
                    if not employee:
                        continue
                    if AZKAttendance.search([('device_id', '=', emp_device_id), ('punching_time', '=', atten_time)]):
                        continue
                    import_status = 'imported'
                    punch_type, _, _ = ZkMachine.resolve_punchtype(a_rec.timestamp, employee)
                    prev = HRAttendance.search([('employee_id', '=', employee.id), ('check_out', '=', False)], limit=1)
                    if punch_type == 'checkin':
                        has_att = emp_cache.get(employee.id, bool(HRAttendance.search([('employee_id', '=', employee.id)], limit=1)))
                        emp_cache[employee.id] = has_att
                        if not has_att:
                            HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
                            emp_cache[employee.id] = True
                            checkins += 1
                        elif not prev:
                            if not HRAttendance.search([('employee_id', '=', employee.id), ('check_in', '=', atten_time)], limit=1):
                                HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
                            checkins += 1
                        elif prev.check_in.date() < atten_time_ts.date():
                            prev.write({'check_out': prev.check_in})
                            HRAttendance.create({'employee_id': employee.id, 'check_in': atten_time})
                            checkins += 1
                        elif prev.check_in < atten_time_ts and not HRAttendance.search([('employee_id', '=', employee.id), ('check_out', '=', atten_time)], limit=1):
                            prev.write({'check_out': atten_time})
                            checkouts += 1
                        else:
                            import_status = 'skipped'
                    else:
                        if prev and prev.check_in < atten_time_ts and not HRAttendance.search([('employee_id', '=', employee.id), ('check_out', '=', atten_time)], limit=1):
                            prev.write({'check_out': atten_time})
                            checkouts += 1
                        else:
                            import_status = 'skipped'
                    AZKAttendance.create({
                        'employee_id': employee.id, 'device_id': emp_device_id,
                        'attendance_type': str(a_rec.status),
                        'punch_type': '0' if punch_type == 'checkin' else '1' if punch_type == 'checkout' else None,
                        'punching_time': atten_time, 'import_status': import_status,
                        'address_id': self.address_id.id,
                    })
                except Exception:
                    log.error("Failed to import attendance '%s'", a_rec, exc_info=True)
        finally:
            if conn:
                conn.disconnect()
        log.info('Done %s: checkins=%s checkouts=%s in %0.2fs', self.name, checkins, checkouts, aztime.time() - before)
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': 'Download status', 'message': 'Checkins: %s Checkouts: %s' % (checkins, checkouts), 'sticky': False, 'type': 'success'}}

    @staticmethod
    def resolve_punchtype(punch_time, employee):
        cal = employee.resource_calendar_id.attendance_ids.filtered(
            lambda a: a.dayofweek == str(punch_time.weekday()))
        if not cal:
            first_day = employee.resource_calendar_id.attendance_ids[:1].dayofweek
            cal = employee.resource_calendar_id.attendance_ids.filtered(lambda a: a.dayofweek == first_day)
        closest_rec, punch_type, t_delta = cal[0], 'checkin', None
        for c in cal:
            hf, mf = int(c.hour_from), int(round((c.hour_from - int(c.hour_from)) * 60))
            ht, mt = int(c.hour_to), int(round((c.hour_to - int(c.hour_to)) * 60))
            c_from = datetime.combine(punch_time.date(), time(hour=hf, minute=mf))
            c_to = datetime.combine(punch_time.date(), time(hour=ht, minute=mt))
            df, dt2 = abs(c_from - punch_time), abs(c_to - punch_time)
            if t_delta is None or df < t_delta:
                closest_rec, punch_type, t_delta = c, 'checkin', df
            if dt2 < t_delta:
                closest_rec, punch_type, t_delta = c, 'checkout', dt2
        return punch_type, closest_rec, t_delta

    def find_or_create_employee(self, user):
        emp = self.env['hr.employee'].search([('name', '=', user.name)], limit=1)
        dev_id = str(user.user_id)
        if emp:
            emp.write({'device_id': dev_id})
        elif self.auto_create_employee:
            emp = self.env['hr.employee'].create({'device_id': dev_id, 'name': user.name})
        return emp
