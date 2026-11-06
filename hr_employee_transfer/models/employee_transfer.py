# -*- coding: utf-8 -*-
#############################################################################
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
#############################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError


class EmployeeTransfer(models.Model):
    """Model for managing employee transfers between companies."""
    _name = 'employee.transfer'
    _description = 'Employee Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char(
        help='Name of the Transfer',
        copy=False, default=lambda self: self.env._('New'), readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True,
        help='Select the employee who is being transferred.')
    old_employee_id = fields.Many2one(
        'hr.employee')
    transfer_date = fields.Date(
        default=fields.Date.context_today,
        help="Transfer date")
    transfer_date_str = fields.Char(
        string='Transfer Date (Formatted)', compute='_compute_transfer_date_str')

    @api.depends('transfer_date')
    def _compute_transfer_date_str(self):
        """Compute a formatted string representation of the transfer date."""
        for record in self:
            if record.transfer_date:
                record.transfer_date_str = (
                    record.transfer_date.strftime('%d %b %Y'))
            else:
                record.transfer_date_str = ''

    transfer_company_id = fields.Many2one(
        'res.company', string='Transfer To',
        help="Select the company to which the employee is being transferred",
        copy=False, required=True)
    state = fields.Selection(
        [('draft', 'New'), ('transfer', 'Transferred'),
         ('cancel', 'Cancelled'), ('done', 'Done')],
        string='Status', readonly=True, copy=False, default='draft',
        tracking=True,
        help="""New: Transfer is created and not confirmed.
        Transferred: Transfer is confirmed. Transfer stays in this status until
         the transferred branch receives the employee.
        Done: Employee has joined and been received in the transferred branch.
        Cancelled: Transfer is cancelled.""")
    company_id = fields.Many2one('res.company', string='Company',
        related='employee_id.company_id', compute_sudo=True,
        help="The current company of the employee before the transfer.")
    note = fields.Text(string='Internal Notes',
        help="Enter any relevant notes regarding the transfer process or "
             "reasons for transfer.")
    transferred = fields.Boolean(copy=False, help="Transferred",
        default=False, compute='_compute_transferred')
    responsible_employee_id = fields.Many2one(comodel_name='hr.employee', string='Responsible',
        default=lambda self: self.env['hr.employee'].sudo().with_context(
            active_test=False).search(
            [('user_id', '=', self.env.uid)], limit=1),
        readonly=True,
        help="The person responsible for the transfer.")
    new_department_id = fields.Many2one(
        'hr.department', string='Target Department',
        help="The department the employee will be transferred to.")
    new_job_id = fields.Many2one(
        'hr.job', string='Target Job Position',
        help="The job position the employee will hold after transfer.")
    new_work_location_id = fields.Many2one(
        'hr.work.location', string='Target Work Location',
        help="The work location after transfer.")
    new_parent_id = fields.Many2one(
        'hr.employee', string='Target Manager',
        help="The manager assigned after transfer.")

    @api.depends('transfer_company_id')
    def _compute_transferred(self):
        """Compute the 'transferred' status for the record."""
        for transfer in self:
            transfer.transferred = (
                transfer.transfer_company_id in transfer.env.user.company_ids)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Update transfer_company_id when employee is selected."""
        if self.employee_id and self.employee_id.company_id:
            if self.transfer_company_id == self.employee_id.company_id:
                self.transfer_company_id = False
            # If exactly one other company exists, auto-populate transfer_co
            other_companies = self.env['res.company'].sudo().search([
                ('id', '!=', self.employee_id.company_id.id)
            ])
            if len(other_companies) == 1 and not self.transfer_company_id:
                self.transfer_company_id = other_companies.id

    @api.onchange('transfer_company_id')
    def _onchange_transfer_company_id(self):
        """Reset target assignment fields if they don't match target co."""
        target_co = self.transfer_company_id
        if (self.new_department_id and self.new_department_id.company_id
                and self.new_department_id.company_id != target_co):
            self.new_department_id = False
        if (self.new_job_id and self.new_job_id.company_id
                and self.new_job_id.company_id != target_co):
            self.new_job_id = False
        if (self.new_work_location_id and self.new_work_location_id.company_id
                and self.new_work_location_id.company_id != target_co):
            self.new_work_location_id = False
        if (self.new_parent_id and self.new_parent_id.company_id
                and self.new_parent_id.company_id != target_co):
            self.new_parent_id = False

    @api.model_create_multi
    def create(self, vals_list):
        """Create an employee transfer record and prefix the 'name' with
        'Transfer: ' followed by the employee's name."""
        for vals in vals_list:
            if vals.get('employee_id'):
                employee = self.env['hr.employee'].browse(vals['employee_id'])
                if employee.exists():
                    vals['name'] = "Transfer: " + (employee.name or "")
        return super().create(vals_list)

    def action_transfer(self):
        """Handle employee transfer logic."""
        self.ensure_one()
        if not self.transfer_company_id:
            raise UserError(self.env._('Please select a company for the transfer.'))
        if self.transfer_company_id == self.company_id:
            raise UserError(
                self.env._('You cannot transfer the employee to the same company.'))
        self.state = 'transfer'

    def action_receive_employee(self):
        """Handle employee reception logic during the transfer."""
        self.ensure_one()
        if self.state != 'transfer':
            raise UserError(self.env._('Only transfers in "Transferred" state can be received.'))
        fields_to_read = [
            'name', 'image_1920', 'private_email', 'sex', 'identification_id',
            'passport_id', 'birthday', 'legal_name', 'place_of_birth',
            'emergency_contact', 'emergency_phone', 'country_id', 'user_id'
        ]
        employee_data = self.employee_id.sudo().read(fields_to_read)[0]
        del employee_data['id']
        if (employee_data.get('country_id')
                and isinstance(employee_data['country_id'], tuple)):
            employee_data['country_id'] = employee_data['country_id'][0]
        if (employee_data.get('user_id')
                and isinstance(employee_data['user_id'], tuple)):
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
            domain.append(
                ('identification_id', '=', employee_data['identification_id']))

        archived_employee = self.env['hr.employee'].sudo().with_context(
            active_test=False).search(domain, limit=1)

        if archived_employee:
            employee_data['active'] = True
            archived_employee.write(employee_data)
            new_employee = archived_employee
        else:
            new_employee = self.env['hr.employee'].sudo().with_company(
                self.transfer_company_id).create(employee_data)

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
        self.ensure_one()
        self.state = 'cancel'


class HrDepartment(models.Model):
    """Inherits hr.department to bypass multi-company access restrictions
    when searching and reading departments during cross-company
    employee transfers."""
    _inherit = 'hr.department'

    @api.model
    def web_name_search(
        self, name='', specification=None, domain=None, operator='ilike',
        limit=100
    ):
        """Perform name search for web views with elevated rights if
        transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_name_search(
            name=name, specification=specification, domain=domain,
            operator=operator, limit=limit
        )

    @api.model
    def web_search_read(
        self, domain=None, specification=None, offset=0, limit=None,
        order=None, count_limit=None
    ):
        """Fetch records with field specifications for web views with
        elevated rights if transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_search_read(
            domain=domain, specification=specification, offset=offset,
            limit=limit, order=order, count_limit=count_limit
        )

    @api.model
    def search_fetch(
        self, domain, field_names=None, offset=0, limit=None, order=None
    ):
        """Fetch records matching domain with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def name_search(
        self, name='', domain=None, operator='ilike', limit=100
    ):
        """Search for departments by name with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )

    def read(self, fields=None, load='_classic_read'):
        """Read department fields with elevated rights if transfer bypass
        is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().read(fields=fields, load=load)

    def check_access(self, operation: str) -> None:
        """Bypass security checks for read operations when
        employee_transfer_bypass is set."""
        if (self.env.context.get('employee_transfer_bypass')
                and operation == 'read'):
            return
        return super().check_access(operation)


class HrJob(models.Model):
    """Inherits hr.job to bypass multi-company access restrictions
    when searching and reading job positions during cross-company
    employee transfers."""
    _inherit = 'hr.job'

    @api.model
    def web_name_search(
        self, name='', specification=None, domain=None, operator='ilike',
        limit=100
    ):
        """Perform name search for web views with elevated rights if
        transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_name_search(
            name=name, specification=specification, domain=domain,
            operator=operator, limit=limit
        )

    @api.model
    def web_search_read(
        self, domain=None, specification=None, offset=0, limit=None,
        order=None, count_limit=None
    ):
        """Fetch records with field specifications for web views with
        elevated rights if transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_search_read(
            domain=domain, specification=specification, offset=offset,
            limit=limit, order=order, count_limit=count_limit
        )

    @api.model
    def search_fetch(
        self, domain, field_names=None, offset=0, limit=None, order=None
    ):
        """Fetch records matching domain with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def name_search(
        self, name='', domain=None, operator='ilike', limit=100
    ):
        """Search for job positions by name with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )

    def read(self, fields=None, load='_classic_read'):
        """Read job position fields with elevated rights if transfer bypass
        is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().read(fields=fields, load=load)

    def check_access(self, operation: str) -> None:
        """Bypass security checks for read operations when
        employee_transfer_bypass is set."""
        if (self.env.context.get('employee_transfer_bypass')
                and operation == 'read'):
            return
        return super().check_access(operation)


class HrWorkLocation(models.Model):
    """Inherits hr.work.location to bypass multi-company access restrictions
    when searching and reading work locations during cross-company
    employee transfers."""
    _inherit = 'hr.work.location'

    @api.model
    def web_name_search(
        self, name='', specification=None, domain=None, operator='ilike',
        limit=100
    ):
        """Perform name search for web views with elevated rights if
        transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_name_search(
            name=name, specification=specification, domain=domain,
            operator=operator, limit=limit
        )

    @api.model
    def web_search_read(
        self, domain=None, specification=None, offset=0, limit=None,
        order=None, count_limit=None
    ):
        """Fetch records with field specifications for web views with
        elevated rights if transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_search_read(
            domain=domain, specification=specification, offset=offset,
            limit=limit, order=order, count_limit=count_limit
        )

    @api.model
    def search_fetch(
        self, domain, field_names=None, offset=0, limit=None, order=None
    ):
        """Fetch records matching domain with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def name_search(
        self, name='', domain=None, operator='ilike', limit=100
    ):
        """Search for work locations by name with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )

    def read(self, fields=None, load='_classic_read'):
        """Read work location fields with elevated rights if transfer bypass
        is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().read(fields=fields, load=load)

    def check_access(self, operation: str) -> None:
        """Bypass security checks for read operations when
        employee_transfer_bypass is set."""
        if (self.env.context.get('employee_transfer_bypass')
                and operation == 'read'):
            return
        return super().check_access(operation)


class HrEmployee(models.Model):
    """Inherits hr.employee to bypass multi-company access restrictions
    when searching and reading employee/manager records during cross-company
    employee transfers."""
    _inherit = 'hr.employee'

    @api.model
    def web_name_search(
        self, name='', specification=None, domain=None, operator='ilike',
        limit=100
    ):
        """Perform name search for web views with elevated rights if
        transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_name_search(
            name=name, specification=specification, domain=domain,
            operator=operator, limit=limit
        )

    @api.model
    def web_search_read(
        self, domain=None, specification=None, offset=0, limit=None,
        order=None, count_limit=None
    ):
        """Fetch records with field specifications for web views with
        elevated rights if transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_search_read(
            domain=domain, specification=specification, offset=offset,
            limit=limit, order=order, count_limit=count_limit
        )

    @api.model
    def search_fetch(
        self, domain, field_names=None, offset=0, limit=None, order=None
    ):
        """Fetch records matching domain with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def name_search(
        self, name='', domain=None, operator='ilike', limit=100
    ):
        """Search for employees by name with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )

    def read(self, fields=None, load='_classic_read'):
        """Read employee fields with elevated rights if transfer bypass
        is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().read(fields=fields, load=load)

    def check_access(self, operation: str) -> None:
        """Bypass security checks for read operations when
        employee_transfer_bypass is set."""
        if (self.env.context.get('employee_transfer_bypass')
                and operation == 'read'):
            return
        return super().check_access(operation)


class ResCompany(models.Model):
    """Inherits res.company to bypass multi-company access restrictions
    when searching and reading company records during cross-company
    employee transfers."""
    _inherit = 'res.company'

    @api.model
    def web_name_search(
        self, name='', specification=None, domain=None, operator='ilike',
        limit=100
    ):
        """Perform name search for web views with elevated rights if
        transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_name_search(
            name=name, specification=specification, domain=domain,
            operator=operator, limit=limit
        )

    @api.model
    def web_search_read(
        self, domain=None, specification=None, offset=0, limit=None,
        order=None, count_limit=None
    ):
        """Fetch records with field specifications for web views with
        elevated rights if transfer bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        if specification is None:
            specification = {}
        return super().web_search_read(
            domain=domain, specification=specification, offset=offset,
            limit=limit, order=order, count_limit=count_limit
        )

    @api.model
    def search_fetch(
        self, domain, field_names=None, offset=0, limit=None, order=None
    ):
        """Fetch records matching domain with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().search_fetch(
            domain, field_names, offset=offset, limit=limit, order=order
        )

    @api.model
    def name_search(
        self, name='', domain=None, operator='ilike', limit=100
    ):
        """Search for companies by name with elevated rights if transfer
        bypass is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().name_search(
            name=name, domain=domain, operator=operator, limit=limit
        )

    def read(self, fields=None, load='_classic_read'):
        """Read company fields with elevated rights if transfer bypass
        is enabled."""
        if self.env.context.get('employee_transfer_bypass'):
            self = self.sudo()
        return super().read(fields=fields, load=load)

    def check_access(self, operation: str) -> None:
        """Bypass security checks for read operations when
        employee_transfer_bypass is set."""
        if (self.env.context.get('employee_transfer_bypass')
                and operation == 'read'):
            return
        return super().check_access(operation)
