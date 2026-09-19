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
from odoo import fields, models


class HrEmployee(models.Model):
    """Inherit hr_employee for getting Payslip Counts"""
    _inherit = 'hr.employee'

    slip_ids = fields.One2many('hr.payslip',
                               'employee_id', string='Payslips',
                               readonly=True,
                               help="Choose Payslip for Employee")
    payslip_count = fields.Integer(compute='_compute_payslip_count',
                                   string='Payslip Count',
                                   help="Set Payslip Count")

    def _compute_payslip_count(self):
        """Function for count Payslips"""
        payslip_data = self.env['hr.payslip'].sudo()._read_group(
            [('employee_id', 'in', self.ids)],
            ['employee_id'], ['__count'])
        result = {employee.id: count for employee, count in payslip_data}
        for employee in self:
            employee.payslip_count = result.get(employee.id, 0)
