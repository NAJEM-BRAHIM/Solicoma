# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    virtual_box = fields.Integer('Boxes')
