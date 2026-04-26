# -*- coding: utf-8 -*-
import logging
from odoo import fields, models
from odoo.exceptions import UserError

log = logging.getLogger(__name__)


class CreateMachineUser(models.TransientModel):
    _name = "azk.machine.user.create"
    _description = "Create Machine User"

    employee_ids = fields.Many2many("hr.employee", string="Employees")
    machine_id = fields.Many2one("azk.machine", string="Machine")
    link_if_exists = fields.Boolean(string="Link User If Exists")

    def create_user(self):
        result = {"type": "ir.actions.client", "tag": "display_notification",
                  "params": {"title": "Create status", "message": "", "sticky": True}}
        conn = False
        errors = []
        created_count = 0
        try:
            conn, _ = self.machine_id.connect()
            if conn:
                for record in self.employee_ids:
                    if record.device_id:
                        found_user = self.machine_id.check_user_id_availabilty(record.device_id, conn)
                        if found_user:
                            if found_user.name.lower() == record.name.lower():
                                errors.append("%s with device ID: %s already created." % (record.name, record.device_id))
                            else:
                                errors.append("Device ID: %s already bound to user %s." % (record.device_id, found_user.name))
                        else:
                            try:
                                conn.set_user(name=record.name, user_id=record.device_id)
                                record.message_post(body="User %s created on machine %s with Device Id %s" % (record.name, self.machine_id.name, record.device_id))
                                created_count += 1
                            except Exception as ex:
                                errors.append("Could not create employee %s: %s" % (record.name, str(ex)))
                    else:
                        try:
                            conn.get_users()
                            device_id = conn.next_user_id
                            if self.link_if_exists:
                                user = self.machine_id.check_username_exists(record.name, conn)
                                if user:
                                    record.device_id = user.user_id
                                    msg = "User %s linked on machine %s with Device Id %s" % (record.name, self.machine_id.name, user.user_id)
                                    record.message_post(body=msg)
                                    errors.append(msg)
                                else:
                                    conn.set_user(name=record.name, user_id=str(device_id))
                                    record.device_id = str(device_id)
                                    msg = "User %s created on machine %s with Device Id %s" % (record.name, self.machine_id.name, device_id)
                                    record.message_post(body=msg)
                                    errors.append(msg)
                                    created_count += 1
                            else:
                                conn.set_user(name=record.name, user_id=str(device_id))
                                record.device_id = str(device_id)
                                msg = "User %s created on machine %s with Device Id %s" % (record.name, self.machine_id.name, device_id)
                                record.message_post(body=msg)
                                errors.append(msg)
                                created_count += 1
                        except Exception as ex:
                            errors.append("Could not create employee %s: %s" % (record.name, str(ex)))
        except Exception as e:
            raise UserError(str(e))
        finally:
            if conn:
                conn.disconnect()
        errors.insert(0, "%s Employee(s) created successfully." % created_count)
        result["params"]["message"] = "\n".join(errors)
        return result


class DeleteMachineUser(models.TransientModel):
    _name = "azk.machine.user.delete"
    _description = "Delete Machine User"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    machine_id = fields.Many2one("azk.machine", string="Machine")

    def delete_user(self):
        self.ensure_one()
        conn = False
        try:
            conn, _ = self.machine_id.connect()
            if conn:
                found_user = self.machine_id.check_user_id_availabilty(self.employee_id.device_id, conn)
                if not found_user:
                    raise UserError("User does not exist on machine")
                conn.delete_user(user_id=self.employee_id.device_id)
                device_id_old = self.employee_id.device_id
                self.employee_id.device_id = False
                self.employee_id.message_post(body="User %s deleted from machine %s (Device Id was: %s)" % (self.employee_id.name, self.machine_id.name, device_id_old))
        except UserError:
            raise
        except Exception as ex:
            raise UserError(str(ex))
        finally:
            if conn:
                conn.disconnect()
        return {"type": "ir.actions.client", "tag": "display_notification",
                "params": {"title": "Delete status", "message": "User deleted successfully", "sticky": True}}
