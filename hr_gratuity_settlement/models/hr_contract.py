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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrContract(models.Model):
    """
    Inheriting hr_contract model
    """
    _inherit = 'hr.contract'

    training_info = fields.Text(string='Probationary Info',
                                help='Probationary Info')
    waiting_for_approval = fields.Boolean(string="Waiting for Approval",
                                          help='Waiting for Approval')
    is_approve = fields.Boolean(string="Is Approved", help='Is Approved')
    state = fields.Selection(
        selection=[
            ('draft', 'New'),
            ('probation', 'Probation'),
            ('open', 'Running'),
            ('close', 'Expired'),
            ('cancel', 'Cancelled'),
        ], string="State", help="State of the contract"
    )
    probation_id = fields.Many2one('hr.training', string="Probation",
                                   help="Select the probation")
    half_leave_ids = fields.Many2many('hr.leave',
                                      string="Half Leave", help="Half Leave")
    training_amount = fields.Float(string='Training Amount',
                                   help="amount for the employee during"
                                        " training")
    company_country_id = fields.Many2one('res.country',
                                         string="Company country",
                                         related='company_id.country_id',
                                         readonly=True,
                                         help="Country of the company")
    wage_type = fields.Selection(
        [('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')],
        string="Wage Type", help="wage type")
    hourly_wage = fields.Monetary(string='Hourly Wage', digits=(16, 2),
                                  default=0,
                                  required=True, tracking=True,
                                  help="Employee's hourly gross wage.")

    @api.onchange('trial_date_end')
    def _onchange_trial_date_end(self):
        """
        function used for changing state draft to probation
        when the end of trail date setting
        """
        if self.trial_date_end:
            self.state = 'probation'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """
        function for changing employee id of hr.training
        """
        if self.probation_id and self.employee_id:
            self.probation_id.employee_id = self.employee_id.id

    def action_approve(self):
        """
        function used for changing the state probation into
        running when approves a contract
        """
        self.write({'is_approve': True})
        if self.state == 'probation':
            self.write({'state': 'open',
                        'is_approve': False})

    @api.model
    def create(self, vals_list):
        """
        function for create a record based on probation
        details in a model
        """
        if vals_list['trial_date_end'] and vals_list['state'] == 'probation':
            dtl = self.env['hr.training'].create({
                'employee_id': vals_list['employee_id'],
                'start_date': vals_list['date_start'],
                'end_date': vals_list['trial_date_end'],
            })
            vals_list['probation_id'] = dtl.id
        res = super(HrContract, self).create(vals_list)
        return res

    def write(self, vals):
        """
        function for checking stage changing and creating probation
        record based on contract stage
        """
        if self.state == 'probation':
            if vals.get('state') == 'open' and not self.is_approve:
                raise UserError(_("You cannot change the status of non-approved"
                                  " Contracts"))
            if vals.get('state') == 'cancel' or vals.get(
                    'state') == 'close' or vals.get('state') == 'draft':
                raise UserError(
                    _("You cannot change the status of non-approved Contracts"))
        training_dtl = self.env['hr.training'].search(
            [('employee_id', '=', self.employee_id.id)])
        if training_dtl:
            return super(HrContract, self).write(vals)
        if not training_dtl:
            if self.trial_date_end and self.state == 'probation':
                self.env['hr.training'].create({
                    'employee_id': self.employee_id.id,
                    'start_date': self.date_start,
                    'end_date': self.trial_date_end,
                })
        return super(HrContract, self).write(vals)
