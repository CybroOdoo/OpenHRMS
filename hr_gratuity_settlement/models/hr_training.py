# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TrainingDetails(models.Model):
    _name = 'hr.training'
    _rec_name = 'employee_id'
    _description = 'HR Training'

    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    start_date = fields.Date(string="Start Date", help="Probation starting date")
    end_date = fields.Date(string="End Date", help="Probation end date")
    state = fields.Selection([('new', 'New'), ('extended', 'Extended')], required=True, default='new')
    leave_ids = fields.Many2many('hr.leave', string="Leaves")




