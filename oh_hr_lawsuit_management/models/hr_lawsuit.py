# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Unnimaya C O (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models


class HrLawsuit(models.Model):
    """Inherited to add more fields and functions"""
    _name = 'hr.lawsuit'
    _description = 'Hr Lawsuit Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Code', help='Name of lawsuit', copy=False)
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 help='Company name of the user')
    requested_date = fields.Date(string='Date', copy=False,
                                 default=fields.date.today(),
                                 help='Start Date')
    hearing_date = fields.Date(string='Hearing Date',
                               help='Date of hearing')
    court_id = fields.Many2one('court.court', string='Court',
                               track_visibility='always',
                               help='Name of the Court')
    judge_id = fields.Many2one('res.partner',
                               related="court_id.judge_id",
                               string='Judge',
                               track_visibility='always',
                               domain="[('is_judge', '=', True)]",
                               help='Name of the Judge')
    lawyer_id = fields.Many2one('res.partner', string='Lawyer',
                                track_visibility='always',
                                help='Choose the Lawyer')
    party1_id = fields.Many2one('res.company', string='Party 1',
                                required=1,
                                default=lambda self: self.env.user.company_id,
                                help='Choose the company as first Party')
    party2 = fields.Selection([('employee', 'Employee'),
                               ('partner', 'Partner'),
                               ('other', 'Others')], string='Party 2',
                              required=1,
                              help='Choose the type of second party of the '
                                   'legal issue.', )
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  copy=False,
                                  help='Choose the Employee')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 copy=False,
                                 help='Choose the partner')
    other_name = fields.Char(string='Name',
                             help='Enter the details of other type')
    case_details = fields.Html(string='Case Details', copy=False,
                               help='More details regarding the case')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('cancel', 'Cancelled'),
                              ('fail', 'Failed'),
                              ('won', 'Won')], string='Status',
                             default='draft', track_visibility='always',
                             copy=False,
                             help='Status of the record')

    @api.model
    def create(self, vals):
        """Inherited to create sequence"""
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.lawsuit')
        return super().create(vals)

    def action_won(self):
        """Method for updating the state to won"""
        self.state = 'won'

    def action_cancel(self):
        """Method for updating the state to cancel"""
        self.state = 'cancel'

    def action_loss(self):
        """Method for updating the state to fail"""
        self.state = 'fail'

    def action_process(self):
        """Method for updating the state to running"""
        self.state = 'running'
