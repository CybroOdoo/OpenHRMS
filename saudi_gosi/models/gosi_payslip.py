# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, fields, models, _


class GosiPayslip(models.Model):
    """This class creates GOSI payslip records"""
    _name = 'gosi.payslip'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'GOSI Record'

    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, default=lambda self: _('New'),
                       help="GOSI Record Reference")
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  required=True, tracking=True, help="Employee")
    department = fields.Char(string="Department",
                             related='employee_id.department_id.name',
                             help="Department")
    position = fields.Char(string='Job Position',
                           related='employee_id.job_id.name',
                           help="Job Position")
    nationality = fields.Char(string='Nationality',
                              related='employee_id.country_id.name',
                              help="Nationality")
    type_gosi = fields.Selection(string='Type',
                                 related='employee_id.type',
                                 readonly=False,
                                 help="GOSI Type")
    dob = fields.Date(string='Date Of Birth',
                      related='employee_id.birthday', help="Date Of Birth")
    gos_numb = fields.Char(string='GOSI Number',
                           related='employee_id.gosi_number',
                           readonly=False,
                           tracking=True, help="GOSI Number")
    issued_dat = fields.Date(string='Issued Date',
                             related='employee_id.issue_date',
                             readonly=False,
                             help="Issued Date")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Warn user if employee has no birthday or is outside eligible GOSI age."""
        if self.employee_id:
            if not self.employee_id.birthday:
                return {
                    'warning': {
                        'title': _("Missing Date of Birth"),
                        'message': _("The employee '%s' does not have a Date of Birth set on their profile. Please set the Date of Birth under Private Information to verify GOSI eligibility.") % self.employee_id.name,
                    }
                }
            elif not self.employee_id.limit:
                return {
                    'warning': {
                        'title': _("Not Eligible for GOSI"),
                        'message': _("The employee '%s' is %s years old. In Saudi Arabia, GOSI contributions apply to employees between 18 and 60 years of age.") % (self.employee_id.name, self.employee_id.age),
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequence number"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gosi.payslip') or _('New')
        return super().create(vals_list)
