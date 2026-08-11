# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EmployeeTransfer(models.Model):
    """Model for managing employee transfers between companies."""
    _name = 'employee.transfer'
    _description = 'Employee Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(
        string='Name', help='Name of the Transfer',
        copy=False, default=lambda self: _('New'), readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        help='Select the employee who is being transferred.')
    old_employee_id = fields.Many2one(
        'hr.employee', string='Old Employee')
    transfer_date = fields.Date(string='Date', default=fields.Date.today(),
                                help="Transfer date")
    transfer_date_str = fields.Char(string='Date', compute='_compute_transfer_date_str')

    @api.depends('transfer_date')
    def _compute_transfer_date_str(self):
        """Compute a formatted string representation of the transfer date."""
        for record in self:
            if record.transfer_date:
                record.transfer_date_str = record.transfer_date.strftime('%d %b %Y')
            else:
                record.transfer_date_str = ''

    transfer_company_id = fields.Many2one(
        'res.company', string='Transfer To',
        help="Select the company to which the employee is being transferred",
        copy=False, required=True)
    state = fields.Selection(
        [('draft', 'New'), ('transfer', 'Transferred'), ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='Status', readonly=True, copy=False, default='draft', tracking=True,
        help="""New: Transfer is created and not confirmed.
        Transferred: Transfer is confirmed. Transfer stays in this status till
         the transferred Branch receive the employee.
        Done: Employee is Joined/Received in the transferred Branch.
        Cancelled: Transfer is cancelled.""")
    company_id = fields.Many2one('res.company', string='Company',
                                 related='employee_id.company_id', compute_sudo=True,
                                 help="The current company of the employee before the transfer.")
    note = fields.Text(
        string='Internal Notes',
        help="Enter any relevant notes regarding the transfer process or reasons for transfer.")
    transferred = fields.Boolean(
        string='Transferred', copy=False, help="Transferred",
        default=False, compute='_compute_transferred')
    responsible_employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Responsible',
        default=lambda self: self.env['hr.employee'].sudo().with_context(active_test=False).search(
            [('user_id', '=', self.env.uid)], limit=1),
        readonly=True,
        help="The person responsible for the transfer.")
    new_department_id = fields.Many2one('hr.department', string='Target Department',
                                        help="The department the employee will be transferred to.")
    new_job_id = fields.Many2one('hr.job', string='Target Job Position',
                                 help="The job position the employee will hold after transfer.")
    new_work_location_id = fields.Many2one('hr.work.location', string='Target Work Location',
                                           help="The work location after transfer.")
    new_parent_id = fields.Many2one('hr.employee', string='Target Manager', help="The manager assigned after transfer.")

    def _compute_transferred(self):
        """Compute the 'transferred' status for the record."""
        self.env.cr.execute("SELECT domain_force FROM ir_rule WHERE name = 'Employee Multi Company Rule'")

        for transfer in self:
            transfer.transferred = transfer.transfer_company_id in transfer.env.user.company_ids

    @api.model
    def create(self, vals_list):
        """Create an employee transfer record and prefix the 'name' with 'Transfer: ' followed by the employee's name."""
        for vals in vals_list:
            employee_id = vals.get('employee_id')
            employee = self.env['hr.employee'].browse(employee_id)
            vals['name'] = "Transfer: " + employee.name
        return super(EmployeeTransfer, self).create(vals_list)

    def action_transfer(self):
        """Handle employee transfer logic."""
        if not self.transfer_company_id:
            raise UserError(_('Please select a company for the transfer.'))
        if self.transfer_company_id == self.company_id:
            raise UserError(_('You cannot transfer the employee to the same company.'))
        self.state = 'transfer'

    def action_receive_employee(self):
        """Handle employee reception logic during the transfer."""
        employee_data = self.employee_id.sudo().read(
            ['name', 'image_1920', 'private_email', 'sex', 'identification_id', 'passport_id', 'birthday', 'legal_name',
             'place_of_birth', 'emergency_contact', 'emergency_phone', 'country_id', 'user_id'])[0]
        del employee_data['id']
        if employee_data.get('country_id') and isinstance(employee_data['country_id'], tuple):
            employee_data['country_id'] = employee_data['country_id'][0]
        if employee_data.get('user_id') and isinstance(employee_data['user_id'], tuple):
            employee_data['user_id'] = employee_data['user_id'][0]

        employee_data.update({
            'company_id': self.transfer_company_id.id
        })

        # Apply target fields if they were provided
        if self.new_department_id:
            employee_data['department_id'] = self.new_department_id.id
        if self.new_job_id:
            employee_data['job_id'] = self.new_job_id.id
        if self.new_work_location_id:
            employee_data['work_location_id'] = self.new_work_location_id.id
        if self.new_parent_id:
            employee_data['parent_id'] = self.new_parent_id.id

        # Check if an archived employee already exists in the target company
        domain = [
            ('company_id', '=', self.transfer_company_id.id),
            ('active', '=', False),
            ('name', '=', employee_data['name'])
        ]
        if employee_data.get('identification_id'):
            domain.append(('identification_id', '=', employee_data['identification_id']))

        archived_employee = self.env['hr.employee'].sudo().with_context(active_test=False).search(domain, limit=1)

        if archived_employee:
            employee_data['active'] = True
            archived_employee.write(employee_data)
            new_employee = archived_employee
        else:
            new_employee = self.env['hr.employee'].sudo().with_company(self.transfer_company_id).create(employee_data)

        # Set the contract start date for the new employee
        new_employee.contract_date_start = self.transfer_date
        self.old_employee_id = self.employee_id
        self.employee_id = new_employee
        self.old_employee_id.sudo().write({
            'active': False,
            'user_id': False
        })
        self.state = 'done'

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def cancel_transfer(self):
        """Transfer cancel function."""
        self.state = 'cancel'


class HrDepartment(models.Model):
    """
    Inherit hr.department to bypass multi-company record rules during employee
    transfers when fetching the target departments.
    """
    _inherit = 'hr.department'

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """
        Override name_search to elevate privileges using sudo() if the custom
        employee_transfer_bypass context is present. This allows users to
        select departments from a target company without manually switching
        their active session.
        """
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(name=name, domain=domain, operator=operator, limit=limit)


class HrJob(models.Model):
    """
    Inherit hr.job to bypass multi-company record rules during employee
    transfers when fetching the target job positions.
    """
    _inherit = 'hr.job'

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """
        Override name_search to elevate privileges using sudo() if the custom
        employee_transfer_bypass context is present. This allows users to
        select job positions from a target company without manually switching
        their active session.
        """
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(name=name, domain=domain, operator=operator, limit=limit)


class HrWorkLocation(models.Model):
    """
    Inherit hr.work.location to bypass multi-company record rules during employee
    transfers when fetching the target work locations.
    """
    _inherit = 'hr.work.location'

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """
        Override name_search to elevate privileges using sudo() if the custom
        employee_transfer_bypass context is present. This allows users to
        select work locations from a target company without manually switching
        their active session.
        """
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(name=name, domain=domain, operator=operator, limit=limit)


class HrEmployee(models.Model):
    """
    Inherit hr.employee to bypass multi-company record rules during employee
    transfers when fetching the target manager.
    """
    _inherit = 'hr.employee'

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        """
        Override name_search to elevate privileges using sudo() if the custom
        employee_transfer_bypass context is present. This allows users to
        select managers from a target company without manually switching
        their active session.
        """
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(name=name, domain=domain, operator=operator, limit=limit)
