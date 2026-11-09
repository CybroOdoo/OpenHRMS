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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, fields, models


class HourlyCost(models.Model):
    """Model  for tracking hourly cost history information."""
    _name = 'hourly.cost'
    _description = 'Hourly Cost'
    _order = 'updated_date desc, id desc'
    _rec_name = 'employee_name'

    employee = fields.Char(string='Employee ID', help="ID of the employee "
                                                      "associated with "
                                                      "the hourly cost record.")
    employee_id = fields.Many2one('hr.employee', string='Employee Ref', compute='_compute_employee_id', store=True, readonly=False)
    employee_name = fields.Char(
        help="Name of the employee whose hourly cost is being updated.",
    )
    updated_date = fields.Date(string='Updated On',
                               help="Date when the hourly cost was updated.")
    current_value = fields.Char(string='Current Cost',
                                help="Updated value of the hourly cost.")

    @api.depends('employee')
    def _compute_employee_id(self):
        """
        Compute the actual hr.employee record from the stored employee ID string.
        """
        for rec in self:
            if rec.employee and rec.employee.isdigit():
                rec.employee_id = int(rec.employee)
            elif not rec.employee_id:
                rec.employee_id = False
