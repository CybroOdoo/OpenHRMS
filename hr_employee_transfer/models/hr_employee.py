# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.employee'

    transfer_detail = fields.One2many('transfer.detail', 'employee_id', string='Transfer Details', help="Details of the transfer ")


class TransferDetails(models.Model):

    _name = 'transfer.detail'
    _description = 'Transfer Details'

    employee_id = fields.Many2one('hr.employee', string='Employee', help="Employee")
    date = fields.Date(string='Date', copy=False, help="Date")
    company_id = fields.Many2one('res.company', string='Company', help="Company")
    pre_company = fields.Many2one('res.company', string='Previous Company', help="Previous company")
