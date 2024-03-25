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
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class Service(models.Model):

    _name = 'service.request'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "service_name"

    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    service_name = fields.Char(required=True, string="Reason For Service", help="Service name")
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_get_employee_id, readonly=True, required=True, help="Employee")
    service_date = fields.Datetime(string="date", required=True, help="Service date")
    state = fields.Selection([('draft', 'Draft'),
                              ('requested', 'Requested'),
                              ('assign', 'Assigned'),
                              ('check', 'Checked'),
                              ('reject', 'Rejected'),
                              ('approved', 'Approved')], default='draft', tracking=True, help="State")
    service_executer = fields.Many2one('hr.employee', string='Service Executer', help="Service executer")
    read_only = fields.Boolean(string="check field", compute='get_user')
    tester = fields.One2many('service.execute', 'test', string='tester', help="Tester")
    internal_note = fields.Text(string="internal notes", help="Internal Notes")
    service_type = fields.Selection([('repair', 'Repair'),
                                     ('replace', 'Replace'),
                                     ('updation', 'Updation'),
                                     ('checking', 'Checking'),
                                     ('adjust', 'Adjustment'),
                                     ('other', 'Other')],
                                    string='Type Of Service', required=True, help="Type for the service request")
    service_product = fields.Many2one('product.product', string='Item For Service', required=True, help="Product you want to service")
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('service.request')
        return super(Service, self).create(vals)

    @api.depends('read_only')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('project.group_project_manager'):
            self.read_only = True
        else:
            self.read_only = False

    def submit_reg(self):
        self.ensure_one()
        self.sudo().write({
            'state': 'requested'
        })
        return

    def assign_executer(self):
        self.ensure_one()
        if not self.service_executer:
            raise ValidationError(_("Select Executer For the Requested Service"))
        self.write({
            'state': 'assign'
        })
        vals = {
            'issue': self.service_name,
            'executer': self.service_executer.id,
            'client': self.employee_id.id,
            'executer_product': self.service_product.name,
            'type_service': self.service_type,
            'execute_date': self.service_date,
            'state_execute': self.state,
            'notes': self.internal_note,
            'test': self.id,
        }
        approve = self.env['service.execute'].sudo().create(vals)
        return
    
    def service_approval(self):
        for record in self:
            record.tester.sudo().state_execute = 'approved'
            record.write({
                'state': 'approved'
            })
        return
    
    def service_rejection(self):
        self.write({
            'state': 'reject'
        })
        return


class Executer(models.Model):

    _name = 'service.execute'
    _rec_name = 'issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'issue'

    client = fields.Many2one('hr.employee', string="Client", help="Client")
    executer = fields.Many2one('hr.employee', string='Executer', help="Executer")
    issue = fields.Char(string="Issue", help="Issue")
    execute_date = fields.Datetime(string="Date Of Reporting", help="Date of reporting")
    state_execute = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('assign', 'Assigned')
                                 , ('check', 'Checked'), ('reject', 'Rejected'),
                              ('approved', 'Approved')], tracking=True,)
    test = fields.Many2one('service.request', string='test', help="Test")
    notes = fields.Text(string="Internal notes", help="Internal Notes")
    executer_product = fields.Char(string='Service Item', help="service item")
    type_service = fields.Char(string='Service Type', help="Service type")

    def service_check(self):
        self.test.sudo().state = 'check'
        self.write({
            'state_execute': 'check'
        })
        return
