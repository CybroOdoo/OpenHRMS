# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class GratuityConfiguration(models.Model):
    """ Model for gratuity duration configuration details """
    _name = 'gratuity.configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Gratuity Configuration"
    _rec_name = "name"

    gratuity_accounting_configuration_id = fields.Many2one('hr.gratuity.accounting.configuration')
    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)
    from_year = fields.Float(string="From Year")
    to_year = fields.Float(string="To Year")
    yr_from_flag = fields.Boolean(compute="_compute_yr_field_required",
                                  store=True)
    yr_to_flag = fields.Boolean(compute="_compute_yr_field_required",
                                store=True)

    company_id = fields.Many2one('res.company', 'Company', required=True, help="Company",
                                 index=True,
                                 default=lambda self: self.env.company)
    employee_daily_wage_days = fields.Integer(default=30, help="Total number of employee wage days")
    employee_working_days = fields.Integer(string='Working Days', default=21,
                                           help='Number of working days per month')
    percentage = fields.Float(default=1)

    @api.onchange('from_year', 'to_year')
    def onchange_year(self):
        """ Function to check year configuration """
        if self.from_year and self.to_year:
            if not self.from_year < self.to_year:
                raise UserError(_("Invalid year configuration!"))

    @api.depends('from_year', 'to_year')
    def _compute_yr_field_required(self):
        """ Compute year from and to required """
        for rec in self:
            rec.yr_from_flag = True if not rec.to_year else False
            rec.yr_to_flag = True if not rec.from_year else False
