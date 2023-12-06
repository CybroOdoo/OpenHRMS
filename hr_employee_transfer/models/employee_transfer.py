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
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class EmployeeTransfer(models.Model):
    """Model for managing Employee Transfers."""
    _name = 'employee.transfer'
    _description = 'Employee Transfer'
    _order = "id desc"

    def _default_responsible_employee_id(self):
        """Get the default employee for the responsible_employee_id field
         in employee_transfer."""
        emp_ids = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)])
        return emp_ids and emp_ids[0] or False

    name = fields.Char(
        string='Name', help='Name of the Transfer',
        copy=False, default=lambda self: _('New'), readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        help='Choose the employee you intend to transfer')
    old_employee_id = fields.Many2one(
        'hr.employee', string='Old Employee', help='Old employee details')
    transfer_date = fields.Date(string='Date', default=fields.Date.today(),
                                help="Transfer date")
    transfer_company_id = fields.Many2one(
        'res.company', string='Transfer To',
        help="Select the company to which the employee is being transferred",
        copy=False, required=True)
    state = fields.Selection(
        [('draft', 'New'), ('transfer', 'Transferred'), ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='Status', readonly=True, copy=False, default='draft',
        help="""New: Transfer is created and not confirmed.
        Transferred: Transfer is confirmed. Transfer stays in this status till
         the transferred Branch receive the employee.
        Done: Employee is Joined/Received in the transferred Branch.
        Cancelled: Transfer is cancelled.""")
    company_id = fields.Many2one('res.company', string='Company',
                                 related='employee_id.company_id',
                                 help="Company of transfer")
    note = fields.Text(
        string='Internal Notes',
        help="Specify notes for the transfer if any")
    transferred = fields.Boolean(
        string='Transferred', copy=False, help="Transferred",
        default=False, compute='_compute_transferred')
    responsible_employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Responsible',
        default=_default_responsible_employee_id, readonly=True,
        help="The person responsible for the transfer.")

    def _compute_transferred(self):
        """Compute the 'transferred' status for the record."""
        for transfer in self:
            transfer.transferred = True if \
                transfer.transfer_company_id in transfer.env.user.company_ids \
                else False

    def action_transfer(self):
        """Transfer button function."""
        if not self.transfer_company_id:
            raise UserError(_(
                'You should select a Company.'))
        if self.transfer_company_id == self.company_id:
            raise UserError(_(
                'You cannot transfer an Employee to the same Company.'))
        self.state = 'transfer'
        return {
            'warning': {
                'title': _("Warning"),
                'message': _(
                    "This employee will remains on the same company until the "
                    "Transferred branch accept this transfer request"),
            },
        }

    def action_receive_employee(self):
        """Receive button function."""
        self.old_employee_id = self.employee_id
        employee = self.employee_id.sudo().read(
            ['name', 'private_email', 'gender',
             'identification_id', 'passport_id'])[0]
        del employee['id']
        employee.update({
            'company_id': self.transfer_company_id.id
        })
        new_emp = self.env['hr.employee'].sudo().create(employee)
        for contract in self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id)]):
            if contract.date_end:
                continue
            else:
                contract.write({'date_end': fields.date.today().strftime(
                    DEFAULT_SERVER_DATE_FORMAT)})
        self.employee_id = new_emp
        self.old_employee_id.sudo().write({'active': False})
        return {
            'name': _('Contract'),
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_employee_id': self.employee_id.id,
                        'default_date_start': self.transfer_date,
                        'default_emp_transfer': self.id,
                        }, }

    def cancel_transfer(self):
        """Transfer cancel function."""
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        """Create a new employee transfer record.
        It customizes the 'name' field by prefixing it with "Transfer:
         " followed by the name of the employee being transferred."""
        vals['name'] = "Transfer: " + self.env['hr.employee'].browse(
            vals['employee_id']).name
        return super(EmployeeTransfer, self).create(vals)
