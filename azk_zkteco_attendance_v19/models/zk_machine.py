from datetime import datetime, date, time, timedelta
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
    # v19: password field no longer has `password` attribute on model side;
    # visibility is handled in the view with password="True"
    password = fields.Char('Password', help="Password must be digits.")
    port_num = fields.Integer(string='Port No', required=True)
    serial_num = fields.Char("Serial num", readonly=True)
    timeout = fields.Integer("Connection Timeout", default=10)
    auto_create_employee = fields.Boolean(
        "Auto create employee",
        help="Automatically create the employee on Odoo if not found",
        default=False,
    )

    address_id = fields.Many2one('res.partner', string='Working Address')
    # v19: env.company is preferred over env.user.company_id
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company.id,
    )

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
        found = False
        for user in machine_users:
            if user.user_id == user_id:
                found = user
                break

        return found

    def check_username_exists(self, name, conn=False):
        if not conn:
            conn, _ = self.connect()

        machine_users = conn.get_users()
        found = False
        for user in machine_users:
            if user.name.lower() == name.lower():
                found = user
                break

        return found

    def test_connection(self):
        conn, _ = self.connect()
        res = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection status',
                'message': '',
                'sticky': False,
            }
        }
        if conn:
            conn.disconnect()
            res['params']['message'] = 'SUCCESS'
            res['params']['type'] = 'success'
        else:
            res['params']['message'] = "Failed to connect: {0}".format(self.last_error_msg)
            res['params']['type'] = 'danger'

        return res

    def connect(self):
        """
        Connects and returns a connection object or exception if not connected.
        Requires the ``pyzk`` package (pip install pyzk).

        :return: (connection, ZK) tuple; both are None on failure.
        """
        zk, conn = None, None
        try:
            zk = ZK(
                self.machine_ip,
                port=self.port_num,
                password=self.password,
                timeout=self.timeout,
                ommit_ping=True,
            )
            conn = zk.connect()

            self.last_run_status = True
            self.last_error_msg = None
            self.serial_num = conn.get_serialnumber()
        except Exception as ex:
            log.error(
                "Failed to connect to: %s[%s:%s]",
                self.name, self.machine_ip, self.port_num,
                exc_info=True,
            )
            self.last_run_status = False
            self.last_error_msg = str(ex)

        return conn, zk

    def clear_attendance(self):
        conn = None
        try:
            conn, _ = self.connect()
            if conn:
                conn.clear_attendance()
            else:
                log.warning(
                    "Failed to connect to machine: %s on %s:%s",
                    self.name, self.machine_ip, self.port_num,
                )
        except Exception:
            log.error(
                "Failed to clear attendance for machine: %s on %s:%s",
                self.name, self.machine_ip, self.port_num,
                exc_info=True,
            )
        finally:
            if conn:
                conn.disconnect()

    @api.model
    def cron_download(self):
        machines = self.env['azk.machine'].search([])
        for machine in machines:
            try:
                machine.download_attendance()
            except Exception:
                log.error(
                    "Failed to download attendance for %s[%s:%s]",
                    machine.name, machine.machine_ip, machine.port_num,
                    exc_info=True,
                )

    def download_attendance(self):
        """
        Downloads attendance from the ZK Machine, stores records locally and
        updates hr.attendance check-in / check-out entries.

        Logic infers check-in/out by comparing the previous locally-stored
        record with the current punch timestamp.
        """
        log.info(
            "Downloading attendance started for '%s[%s:%s]'",
            self.name, self.machine_ip, self.port_num,
        )

        AZKAttendance = self.env['azk.machine.attendance']
        HRAttendance = self.env['hr.attendance']

        # v19: prefer env.user.tz (partner tz was deprecated)
        user_tz = self.env.user.tz or self.env.user.partner_id.tz or 'GMT'
        local_tz = pytz.timezone(user_tz)

        conn = None
        total_attendance_rec = total_users = total_checkins = total_checkouts = 0
        before = aztime.time()

        try:
            conn, _ = self.connect()
            if conn:
                lst_attendance = conn.get_attendance()
                machine_users = conn.get_users()

                users_by_id = {u.user_id: u for u in machine_users}
                employees_by_device_id = {
                    e.device_id: e
                    for e in self.env['hr.employee'].search(
                        [('device_id', 'in', [u.user_id for u in machine_users])]
                    )
                }

                total_attendance_rec = len(lst_attendance)
                total_users = len(machine_users)

                # Remove future-dated records
                today = datetime.today().date()
                lst_attendance = [a for a in lst_attendance if a.timestamp.date() <= today]

                # Only re-import from 3 days before the last imported record
                latest_imported = AZKAttendance.search([], order="punching_time desc", limit=1)
                cut_off_date = None
                if latest_imported:
                    cut_off_date = latest_imported.punching_time - timedelta(days=3)
                    lst_attendance = [a for a in lst_attendance if a.timestamp > cut_off_date]

                log.info(
                    "Got %s attendance entries and %s users from: %s[%s:%s] "
                    "importing from: %s -> %s rec to import",
                    total_attendance_rec, len(machine_users),
                    self.name, self.machine_ip, self.port_num,
                    cut_off_date, len(lst_attendance),
                )

                employees_with_attendance = {}

                for a_rec in sorted(lst_attendance, key=lambda a: a.timestamp):
                    try:
                        atten_time = a_rec.timestamp
                        emp_device_id = str(a_rec.user_id)

                        try:
                            local_dt = local_tz.localize(atten_time, is_dst=None)
                        except pytz.exceptions.AmbiguousTimeError:
                            local_dt = local_tz.localize(atten_time, is_dst=True)

                        utc_dt = local_dt.astimezone(pytz.utc)
                        utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")

                        atten_time_ts = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                        # v19: fields.Datetime.to_string still works but
                        # storing a datetime object directly is also accepted.
                        atten_time = fields.Datetime.to_string(atten_time_ts)

                        employee = employees_by_device_id.get(emp_device_id)
                        if not employee:
                            employee = (
                                self.find_or_create_employee(users_by_id[emp_device_id])
                                if emp_device_id in users_by_id
                                else False
                            )
                            employees_by_device_id[emp_device_id] = employee

                        if employee:
                            duplicate_atten_ids = AZKAttendance.search([
                                ('device_id', '=', emp_device_id),
                                ('punching_time', '=', atten_time),
                            ])

                            if not duplicate_atten_ids:
                                import_status = 'imported'
                                punch_type, _, _ = ZkMachine.resolve_punchtype(
                                    a_rec.timestamp, employee
                                )

                                previous_check_in = HRAttendance.search([
                                    ('employee_id', '=', employee.id),
                                    ('check_out', '=', False),
                                ], limit=1)

                                if punch_type == 'checkin':
                                    if employee.id in employees_with_attendance:
                                        emp_has_attendance_rec = employees_with_attendance[employee.id]
                                    else:
                                        emp_has_attendance_rec = bool(
                                            HRAttendance.search(
                                                [('employee_id', '=', employee.id)], limit=1
                                            )
                                        )
                                        employees_with_attendance[employee.id] = emp_has_attendance_rec

                                    if not emp_has_attendance_rec:
                                        HRAttendance.create({
                                            'employee_id': employee.id,
                                            'check_in': atten_time,
                                        })
                                        employees_with_attendance[employee.id] = True
                                        total_checkins += 1
                                    elif not previous_check_in:
                                        if not HRAttendance.search([
                                            ('employee_id', '=', employee.id),
                                            ('check_in', '=', atten_time),
                                        ], limit=1):
                                            HRAttendance.create({
                                                'employee_id': employee.id,
                                                'check_in': atten_time,
                                            })
                                        total_checkins += 1
                                    elif previous_check_in.check_in.date() < atten_time_ts.date():
                                        previous_check_in.write({
                                            'check_out': previous_check_in.check_in
                                        })
                                        HRAttendance.create({
                                            'employee_id': employee.id,
                                            'check_in': atten_time,
                                        })
                                        total_checkins += 1
                                    elif (
                                        previous_check_in.check_in < atten_time_ts
                                        and not HRAttendance.search([
                                            ('employee_id', '=', employee.id),
                                            ('check_out', '=', atten_time),
                                        ], limit=1)
                                    ):
                                        previous_check_in.write({'check_out': atten_time})
                                        total_checkouts += 1
                                    else:
                                        import_status = 'skipped'
                                else:
                                    if (
                                        previous_check_in
                                        and previous_check_in.check_in < atten_time_ts
                                        and not HRAttendance.search([
                                            ('employee_id', '=', employee.id),
                                            ('check_out', '=', atten_time),
                                        ], limit=1)
                                    ):
                                        previous_check_in.write({'check_out': atten_time})
                                        total_checkouts += 1
                                    else:
                                        import_status = 'skipped'

                                AZKAttendance.create({
                                    'employee_id': employee.id,
                                    'device_id': emp_device_id,
                                    'attendance_type': str(a_rec.status),
                                    'punch_type': (
                                        '0' if punch_type == 'checkin'
                                        else '1' if punch_type == 'checkout'
                                        else None
                                    ),
                                    'punching_time': atten_time,
                                    'import_status': import_status,
                                    'address_id': self.address_id.id,
                                })

                                if import_status == 'skipped':
                                    log.info(
                                        "Skip updating attendance for %s "
                                        "prev checkin: %s, detected punch type: '%s'",
                                        a_rec, previous_check_in, punch_type,
                                    )

                                if ((total_checkins + total_checkouts) % 100) == 0:
                                    log.info(
                                        "Imported so far: %s checkins and %s checkouts "
                                        "out of %s total",
                                        total_checkins, total_checkouts, total_attendance_rec,
                                    )
                        else:
                            log.info(
                                "Skip adding attendance: %s for user: %s. "
                                "Make sure employee is created, device_id is set "
                                "and Auto create employee is enabled.",
                                a_rec, users_by_id.get(emp_device_id),
                            )
                    except Exception:
                        log.error(
                            "Failed to import attendance '%s' for '%s'",
                            a_rec, self.name,
                            exc_info=True,
                        )
            else:
                log.warning("Failed to connect to %s", self.name)
        finally:
            if conn:
                conn.disconnect()

        log.info(
            'Finish import machine %s -> %s attendance records for %s users. '
            'Checkins: %s and Checkouts: %s in %0.2fs',
            self.name, total_attendance_rec, total_users,
            total_checkins, total_checkouts,
            aztime.time() - before,
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Download status',
                'message': (
                    'Imported %s attendance records for %s users. '
                    'Checkins: %s and Checkouts: %s'
                    % (total_attendance_rec, total_users, total_checkins, total_checkouts)
                ),
                'sticky': False,
                'type': 'success',
            },
        }

    @staticmethod
    def resolve_punchtype(punch_time, employee):
        """
        Determine whether a punch is a check-in or check-out based on the
        employee's working-hours calendar.

        :param punch_time: naive datetime from the ZK device (local time)
        :param employee: hr.employee record
        :return: ('checkin'|'checkout', calendar.attendance record, timedelta)
        """
        cal_attendance = employee.resource_calendar_id.attendance_ids.filtered(
            lambda a: a.dayofweek == str(punch_time.weekday())
        )
        if not cal_attendance:
            first_day = employee.resource_calendar_id.attendance_ids[:1].dayofweek
            cal_attendance = employee.resource_calendar_id.attendance_ids.filtered(
                lambda a: a.dayofweek == first_day
            )

        closest_rec = cal_attendance[0]
        punch_type = 'checkin'
        t_delta_sec = None

        for c_att in cal_attendance:
            hour_from_int = int(c_att.hour_from)
            min_from = int(round((c_att.hour_from - hour_from_int) * 60))
            hour_to_int = int(c_att.hour_to)
            min_to = int(round((c_att.hour_to - hour_to_int) * 60))

            c_from = datetime.combine(punch_time.date(), time(hour=hour_from_int, minute=min_from))
            c_to = datetime.combine(punch_time.date(), time(hour=hour_to_int, minute=min_to))

            delta_from = abs(c_from - punch_time)
            delta_to = abs(c_to - punch_time)

            if t_delta_sec is None or delta_from < t_delta_sec:
                closest_rec = c_att
                punch_type = 'checkin'
                t_delta_sec = delta_from

            if delta_to < t_delta_sec:
                closest_rec = c_att
                punch_type = 'checkout'
                t_delta_sec = delta_to

        return punch_type, closest_rec, t_delta_sec

    def find_or_create_employee(self, user):
        """
        Search for an employee by name; if found, update their device_id.
        If not found and ``auto_create_employee`` is enabled, create them.

        :param user: pyzk User object
        :return: hr.employee record or False
        """
        employee = self.env['hr.employee'].search([('name', '=', user.name)], limit=1)
        emp_device_id = str(user.user_id)

        if employee:
            employee.write({'device_id': emp_device_id})
        elif self.auto_create_employee:
            employee = self.env['hr.employee'].create({
                'device_id': emp_device_id,
                'name': user.name,
            })

        return employee
