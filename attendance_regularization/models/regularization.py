# -*- coding: utf-8 -*-
from odoo import fields, api, models


class Regular(models.Model):

    _name = 'attendance.regular'
    _rec_name = 'employee'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    reg_category = fields.Selection([('onsight', 'On Sight Job')],
                                    string='Regularization Category', required=True)
    from_date = fields.Datetime(string='From Date', required=True)
    to_date = fields.Datetime(string='To Date', required=True)
    reg_reason = fields.Text(string='Reason', required=True)
    employee = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id, readonly=True, required=True)
    state_select = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('reject', 'Rejected'),
                                     ('approved', 'Approved')
                                     ], default='draft', track_visibility='onchange', string='State')

    @api.multi
    def submit_reg(self):
        self.ensure_one()
        self.sudo().write({
            'state_select': 'requested'
        })
        return

    @api.multi
    def regular_approval(self):
        self.write({
            'state_select': 'approved'
        })
        vals = {

            'check_in': self.from_date,
            'check_out': self.to_date,
            'employee_id': self.employee.id

        }
        approve = self.env['hr.attendance'].sudo().create(vals)
        return

    @api.multi
    def regular_rejection(self):
        self.write({
            'state_select': 'reject'
        })
        return




