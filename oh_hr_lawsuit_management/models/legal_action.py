# -*- coding: utf-8 -*-

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
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    requested_date = fields.Date(string='Date', copy=False, readonly=1,
                                 states={'draft': [('readonly', False)]})
    court_name = fields.Char(string='Court Name', track_visibility='always',
                             states={'won': [('readonly', True)]})
    judge = fields.Char(string='Judge', track_visibility='always', states={'won': [('readonly', True)]})
    lawyer = fields.Char(string='Lawyer', track_visibility='always', states={'won': [('readonly', True)]})
    party1 = fields.Many2one('res.company', string='Party 1', required=1, readonly=1,
                             states={'draft': [('readonly', False)]})
    party2 = fields.Selection([('employee', 'Employee')], default='employee',
                              string='Party 2', required=1, readonly=1, states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', copy=False,
                                  readonly=1, states={'draft': [('readonly', False)]})
    party2_name = fields.Char(compute='set_party2', string='Name', store=True)
    case_details = fields.Html(string='Case Details', copy=False, track_visibility='always')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('cancel', 'Cancelled'),
                              ('fail', 'Failed'),
                              ('won', 'Won')], string='Status',
                             default='draft', track_visibility='always', copy=False)


class HrLegalEmployeeMaster(models.Model):
    _inherit = 'hr.employee'

    legal_count = fields.Integer(compute='_legal_count', string='# Legal Actions')

    
    def _legal_count(self):
        for each in self:
            legal_ids = self.env['hr.lawsuit'].search([('employee_id', '=', each.id)])
            each.legal_count = len(legal_ids)

    
    def legal_view(self):
        for each1 in self:
            legal_obj = self.env['hr.lawsuit'].sudo().search([('employee_id', '=', each1.id)])
            legal_ids = []
            for each in legal_obj:
                legal_ids.append(each.id)
            view_id = self.env.ref('oh_hr_lawsuit_management.hr_lawsuit_form_view').id
            if legal_ids:
                if len(legal_ids) <= 1:
                    value = {
                        'res_model': 'hr.lawsuit',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Legal Actions'),
                        'res_id': legal_ids and legal_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', legal_ids)]),
                        'view_mode': 'tree,form',
                        'res_model': 'hr.lawsuit',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Legal Actions'),
                        'res_id': legal_ids
                    }

                return value


