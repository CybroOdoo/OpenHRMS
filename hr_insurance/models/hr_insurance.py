# -*- coding: utf-8 -*-
#############################################################################
#   A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class HrInsurance(models.Model):
    """Created a new model for employee insurance"""
    _name = 'hr.insurance'
    _description = 'HR Insurance'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True, help="Employee")
    policy_id = fields.Many2one('insurance.policy',
                                string='Policy', required=True, help="Policy")
    amount = fields.Float(string='Premium', required=True, help="Policy amount")
    sum_insured = fields.Float(string="Sum Insured", required=True,
                               help="Insured sum")
    policy_coverage = fields.Selection([('monthly', 'Monthly'),
                                        ('yearly', 'Yearly')],
                                       required=True, default='monthly',
                                       string='Policy Coverage',
                                       help="Duration of the policy")
    date_from = fields.Date(string='Date From',
                            default=fields.date.today(), readonly=True,
                            help="Start date")
    date_to = fields.Date(string='Date To', help="End date")
    state = fields.Selection([('active', 'Active'),
                              ('expired', 'Expired'), ],
                             default='active', string="State",
                             compute='_compute_status',
                             help="State for the insurance")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True, help="Company",
                                 default=lambda self: self.env.user.company_id)

    def _compute_status(self):
        """This function is get and set state"""
        current_date = fields.date.today()
        for rec in self:
            if rec.policy_coverage == 'monthly':
                rec.date_to = fields.Date.end_of(rec.date_from, 'month')
            if rec.policy_coverage == 'yearly':
                rec.date_to = fields.Date.end_of(rec.date_from, 'year')
            if rec.date_from <= current_date:
                if rec.date_to and rec.date_to >= current_date:
                    rec.state = 'active'
                else:
                    rec.state = 'expired'
