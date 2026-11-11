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
from odoo.exceptions import UserError


class HrContract(models.Model):
    """Inheriting hr.version model for contract/version management in Odoo 20"""
    _inherit = 'hr.version'

    training_info = fields.Text(string='Probationary Info',
                                help='Probationary Info of the candidate.')
    waiting_for_approval = fields.Boolean(
        string="Waiting for Approval",
        help='Is true, the candidate is waiting for approval')
    is_approve = fields.Boolean(
        string="Is Approved", help='The candidate has been approved')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('probation', 'Probation'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string="Status", default='draft', tracking=True, help="State of the contract")
    probation_id = fields.Many2one('hr.training', string="Probation",
                                   help="Select the probation for the candidate.")
    half_leave_ids = fields.Many2many(
        'hr.leave', string="Half Leave",
        help="Half Leaves of the candidate.")
    training_amount = fields.Float(
        string='Training Amount', help="amount for the employee during training")
    wage_type = fields.Selection(
        [('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')],
        string="Wage Type", default='monthly', tracking=True, help="Wage type of the employee.")
    hourly_wage = fields.Monetary(
        string='Hourly Wage', default=0,
        tracking=True, help="Employee's hourly gross wage.")

    @api.model
    def _get_whitelist_fields_from_template(self):
        whitelist = super()._get_whitelist_fields_from_template()
        allowance_fields = [
            'wage_type', 'hourly_wage', 'hra', 'da', 'travel_allowance',
            'meal_allowance', 'medical_allowance', 'other_allowance'
        ]
        return whitelist + allowance_fields

    def _get_contract_wage_field(self):
        self.ensure_one()
        if self.wage_type == 'hourly':
            return 'hourly_wage'
        return super()._get_contract_wage_field()

    @api.onchange('trial_date_end')
    def _onchange_trial_date_end(self):
        """function used for changing state draft to probation
        when the end of trail date setting"""
        if self.trial_date_end:
            self.state = 'probation'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """function for changing employee id of hr.training"""
        if self.probation_id and self.employee_id:
            self.probation_id.employee_id = self.employee_id.id

    def action_approve(self):
        """function used for changing the state probation into
        running when approves a contract"""
        self.write({'is_approve': True})
        if self.state == 'probation':
            self.write({'state': 'open',
                        'is_approve': False})

    @api.model_create_multi
    def create(self, vals_list):
        """function for create a record based on probation
        details in a model """
        for vals in vals_list:
            if vals.get('trial_date_end') and vals.get('state') == 'probation':
                start_date = (vals.get('contract_date_start') or
                              vals.get('date_start') or
                              vals.get('date_version'))
                dtl = self.env['hr.training'].create([{
                    'employee_id': vals.get('employee_id'),
                    'start_date': start_date,
                    'end_date': vals.get('trial_date_end'),

                }])
                vals['probation_id'] = dtl.id
        return super().create(vals_list)

    def write(self, vals):
        """function for checking stage changing and creating probation
        record based on contract stage"""
        if self.state == 'probation':
            if vals.get('state') == 'open' and not self.is_approve:
                raise UserError(_("You cannot change the status of non-approved"
                                  " Contracts"))
            if vals.get('state') in ('cancel', 'close', 'draft'):
                raise UserError(
                    _("You cannot change the status of non-approved Contrac.ts"))
        training_dtl = self.env['hr.training'].search(
            [('employee_id', '=', self.employee_id.id)])
        if training_dtl:
            return super().write(vals)
        if not training_dtl:
            if ((vals.get('trial_date_end') or self.trial_date_end) and
                    (vals.get('state') == 'probation' or self.state == 'probation')):
                start_date = (vals.get('contract_date_start') or
                              self.contract_date_start or
                              self.date_start or
                              self.date_version)
                end_date = vals.get('trial_date_end') or self.trial_date_end
                if start_date and end_date:
                    self.env['hr.training'].create([{
                        'employee_id': self.employee_id.id,
                        'start_date': start_date,
                        'end_date': end_date,
                    }])
        return super().write(vals)
