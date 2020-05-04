# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeEntryDocuments(models.Model):
    _name = 'employee.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"
    _order = 'sequence'

    name = fields.Char(string='Name', copy=False, required=1, help="Checklist Name")
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')], string='Checklist Type', help='Type of Checklist', required=1)
    sequence = fields.Integer('Sequence')


class HrEmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    document_name = fields.Many2one('employee.checklist', string='Document', help='Type of Document', required=True)

