# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class GratuityConfiguration(models.Model):
    """ Model for gratuity duration configuration details """
    _name = 'gratuity.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Gratuity Configuration"
    _rec_name = "name"

    gratuity_accounting_configuration_id = fields.Many2one(
        'hr.gratuity.accounting.configuration',
        string="Gratuity Accounting Configuration",
        help="Gratuity Accounting Configuration")
    name = fields.Char(string="Name", required=True, copy=True, help="Name")
    active = fields.Boolean(default=True, string="active", help="Is it active")
    from_year = fields.Float(string="From Year", copy=True, help="From Year")
    to_year = fields.Float(string="To Year", copy=True, help="To Year")
    yr_from_flag = fields.Boolean(compute="_compute_yr_from_flag",
                                  store=True, string="Year from flag",
                                  help="Year from flag")
    yr_to_flag = fields.Boolean(compute="_compute_yr_from_flag",
                                store=True, string="Year to flag",
                                help="Year to flag")
    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 help="Default Company",
                                 index=True,
                                 default=lambda self: self.env.company)
    employee_daily_wage_days = fields.Integer(default=30,
                                              string="Employee wage days",
                                              help="Total number of employee"
                                                   " wage days")
    employee_working_days = fields.Integer(string='Working Days', default=21,
                                           help='Number of working days per'
                                                ' month')
    percentage = fields.Float(default=1, string="Percentage",
                              help="Add the percentage")

    @api.onchange('from_year', 'to_year')
    def _onchange_from_year(self):
        """ Function to check year configuration """
        if self.from_year and self.to_year:
            if not self.from_year < self.to_year:
                raise UserError(_("Invalid year configuration!"))

    @api.depends('from_year', 'to_year')
    def _compute_yr_from_flag(self):
        """ Compute year from and to required """
        for rec in self:
            rec.yr_from_flag = True if not rec.to_year else False
            rec.yr_to_flag = True if not rec.from_year else False
