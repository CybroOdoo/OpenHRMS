# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from datetime import datetime
from odoo import models, fields, api, _


class HrLawsuit(models.Model):
    _name = 'hr.lawsuit'
    _description = 'Hr Lawsuit Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.lawsuit')
        return super(HrLawsuit, self).create(vals)

    def won(self):
        self.state = 'won'

    def cancel(self):
        self.state = 'cancel'

    def loss(self):
        self.state = 'fail'

    def process(self):
        self.state = 'running'

    @api.depends('party2', 'employee_id')
    def set_party2(self):
        for each in self:
            if each.party2 == 'employee':
                each.party2_name = each.employee_id.name

    name = fields.Char(string='Code', copy=False)
    ref_no = fields.Char(string="Reference Number")
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 help='Name of the company of the user')
    requested_date = fields.Date(string='Date', copy=False, readonly=1,
                                 help='Start Date',
                                 states={'draft': [('readonly', False)]})
    hearing_date = fields.Date(string='Hearing Date',
                               help='Upcoming hearing date')
    court_name = fields.Char(string='Court Name', track_visibility='always',
                             states={'won': [('readonly', True)]},
                             help='Name of the Court')
    judge = fields.Char(string='Judge', track_visibility='always',
                        states={'won': [('readonly', True)]},
                        help='Name of the Judge')
    lawyer = fields.Many2one('res.partner', string='Lawyer',
                             track_visibility='always',
                             help='Choose the contact of Layer from the contact list',
                             states={'won': [('readonly', True)]})
    party1 = fields.Many2one('res.company', string='Party 1', required=1,
                             readonly=1,
                             help='Choose the company as first Party',
                             states={'draft': [('readonly', False)]})
    party2 = fields.Selection([('employee', 'Employee'),
                               ('partner', 'Partner'),
                               ('other', 'Others')], default='employee',
                              string='Party 2', required=1, readonly=1,
                              help='Choose the second party in the legal issue.It can be Employee, Contacts or others.',
                              states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', copy=False,
                                  readonly=1,
                                  states={'draft': [('readonly', False)]},
                                  help='Choose the Employee')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 copy=False,
                                 readonly=1,
                                 states={'draft': [('readonly', False)]},
                                 help='Choose the partner')
    other_name = fields.Char(string='Name',
                             help='Enter the details of other type')
    party2_name = fields.Char(compute='set_party2', string='Name', store=True)
    case_details = fields.Html(string='Case Details', copy=False,
                               track_visibility='always',
                               help='More details of the case')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('cancel', 'Cancelled'),
                              ('fail', 'Failed'),
                              ('won', 'Won')], string='Status',
                             default='draft', track_visibility='always',
                             copy=False,
                             help='Status')


class HrLegalEmployeeMaster(models.Model):
    _inherit = 'hr.employee'

    legal_count = fields.Integer(compute='_legal_count',
                                 string='# Legal Actions', help='Legal actions')

    def _legal_count(self):
        for each in self:
            legal_ids = self.env['hr.lawsuit'].search(
                [('employee_id', '=', each.id)])
            each.legal_count = len(legal_ids)

    def legal_view(self):
        for employee in self:
            legal_ids = self.env['hr.lawsuit'].sudo().search(
                [('employee_id', '=', employee.id)]).ids
            return {
                'domain': str([('id', 'in', legal_ids)]),
                'view_mode': 'tree,form',
                'res_model': 'hr.lawsuit',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'name': _('Legal Actions'),
            }
