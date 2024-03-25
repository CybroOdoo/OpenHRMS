# -*- coding: utf-8 -*-
###############################################################################
#
#   Cybrosys Technologies Pvt. Ltd.
#
#   Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#   Author: Hajaj( odoo@cybrosys.com )
#
#   You can modify it under the terms of the GNU AFFERO
#   GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#   You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#   (AGPL v3) along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class EmployeeTransfer(models.Model):
    _name = 'employee.transfer'
    _description = 'Employee Transfer'
    _order = "id desc"

    def _default_employee(self):
        emp_ids = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    name = fields.Char(
        string='Name', help='Give a name to the Transfer',
        copy=False, default=lambda self: _('New'), readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        help='Select the employee you are going to transfer')
    old_employee_id = fields.Many2one(
        'hr.employee', string='Old Employee', Help='Old employee details')
    date = fields.Date(string='Date', default=fields.Date.today(), help="Date")
    transfer_company_id = fields.Many2one(
        'res.company', string='Transfer To', help="Transferring Company",
        copy=False, required=True)
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'),
         ('transfer', 'Transferred'), ('done', 'Done')],
        string='Status', readonly=True, copy=False, default='draft',
        help=" * The 'Draft' status is used when a transfer is created and unconfirmed Transfer.\n"
             " * The 'Transferred' status is used when the user confirm the transfer. It stays in the open status till the other company receive the employee.\n"
             " * The 'Done' status is set automatically when the employee is Joined/Received.\n"
             " * The 'Cancelled' status is used when user cancel Transfer.")
    company_id = fields.Many2one(
        'res.company', string='Company', related='employee_id.company_id',
        help="Company")
    note = fields.Text(
        string='Internal Notes',
        help="Specify notes for the transfer if any")
    transferred = fields.Boolean(
        string='Transferred', copy=False, help="Transferred",
        default=False, compute='_compute_transferred',)
    responsible = fields.Many2one(
        'hr.employee', string='Responsible', default=_default_employee,
        readonly=True, help="Responsible person for the transfer")

    def _compute_transferred(self):
        for rec in self:
            rec.transferred = True if \
                rec.transfer_company_id in rec.env.user.company_ids else False

    def transfer(self):
        if not self.transfer_company_id:
            raise UserError(_(
                'You should select the company.'))
        if self.transfer_company_id == self.company_id:
            raise UserError(_(
                'You cannot transfer to the same company.'))
        self.state = 'transfer'
        return {
            'warning': {
                'title': _("Warning"),
                'message': _(
                    "This employee will remains on the same company until the "
                    "Transferred company accept this transfer request"),
            },
        }

    def receive_employee(self):
        self.old_employee_id = self.employee_id
        emp = self.employee_id.sudo().read(
            ['name', 'private_email', 'gender',
             'identification_id', 'passport_id'])[0]
        del emp['id']
        emp.update({
            'company_id': self.transfer_company_id.id
        })
        new_emp = self.env['hr.employee'].sudo().create(emp)
        if self.employee_id.address_home_id:
            self.employee_id.address_home_id.active = False
        for contract in self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id)]):
            if contract.date_end:
                continue
            else:
                contract.write({'date_end': date.today().strftime(
                    DEFAULT_SERVER_DATE_FORMAT)})
        self.employee_id = new_emp
        self.old_employee_id.sudo().write({'active': False})
        partner = {
            'name': self.employee_id.name,
            'company_id': self.transfer_company_id.id,
        }
        partner_created = self.env['res.partner'].create(partner)
        self.employee_id.sudo().write({'address_home_id': partner_created.id})
        return {
            'name': _('Contract'),
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_employee_id': self.employee_id.id,
                        'default_date_start': self.date,
                        'default_emp_transfer': self.id,
                        },
        }

    def cancel_transfer(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = "Transfer: " + self.env['hr.employee'].browse(
            vals['employee_id']).name
        res = super(EmployeeTransfer, self).create(vals)
        return res
