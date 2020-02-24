from odoo import fields, api, models


class Regular(models.Model):
    _name = 'attendance.regular'
    _rec_name = 'employee_id'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    reg_category = fields.Many2one('reg.categories', string='Regularization Category', required=True,
                                   help='Choose the category of attendance regularization')
    from_date = fields.Datetime(string='From Date', required=True, help='Start Date')
    to_date = fields.Datetime(string='To Date', required=True, help='End Date')
    reg_reason = fields.Text(string='Reason', required=True, help='Reason for the attendance regularization')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id, readonly=True,
                                  required=True, help='Employee')
    state_select = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('reject', 'Rejected'),
                                     ('approved', 'Approved')
                                     ], default='draft', track_visibility='onchange', string='State',
                                    help='State')

    
    def submit_reg(self):
        self.ensure_one()
        self.sudo().write({
            'state_select': 'requested'
        })
        return

    
    def regular_approval(self):
        self.write({
            'state_select': 'approved'
        })
        vals = {
            'check_in': self.from_date,
            'check_out': self.to_date,
            'employee_id': self.employee_id.id,
            'regularization': True
        }
        approve = self.env['hr.attendance'].sudo().create(vals)
        return

    
    def regular_rejection(self):
        self.write({
            'state_select': 'reject'
        })
        return


class Category(models.Model):
    _name = 'reg.categories'
    _rec_name = 'type'

    type = fields.Char(string='Category', help='Type of regularization')
