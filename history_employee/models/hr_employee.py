# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    """Inherited the 'hr.employee' model to add onchange methods and actions to
    record changes in department, job position, hourly cost, and provides access
     to related historical data for HR employees."""
    _inherit = 'hr.employee'

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Create a record in 'department.history' when the 'department_id'
        field changes."""
        employee_id = self.env['hr.employee'].browse(self._origin.id)
        self.env['department.history'].sudo().create({
            'employee': self._origin.id,
            'employee_name': employee_id.name,
            'updated_date': fields.Datetime.now(),
            'changed_field': 'Department',
            'current_value': self.department_id.name
        })

    @api.onchange('job_id')
    def _onchange_job_id(self):
        """Create a record in 'department.history' when the 'job_id' field
        changes."""
        employee_id = self.env['hr.employee'].browse(self._origin.id)
        self.env['department.history'].sudo().create({
            'employee': self._origin.id,
            'employee_name': employee_id.name,
            'updated_date': fields.Date.today(),
            'changed_field': 'Job Position',
            'current_value': self.job_id.name
        })

    @api.onchange('hourly_cost')
    def _onchange_hourly_cost(self):
        """Create a record in 'hourly.cost' when the 'hourly_cost' field
        changes."""
        employee_id = self.env['hr.employee'].browse(self._origin.id)
        self.env['hourly.cost'].sudo().create({
            'employee': self._origin.id,
            'employee_name': employee_id.name,
            'updated_date': fields.datetime.now(),
            'current_value': self.hourly_cost
        })

    def action_job_history(self):
        """This method checks the user's access rights and redirects to the
        'Job/Department History'
        view if the user has the required access."""
        user_id = self.env['res.users'].browse(self._uid)
        if user_id.has_group('hr.group_hr_manager'):
            return {
                'name': _("Job/Department History"),
                'view_mode': 'tree',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee', '=', self.id)],
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Job/Department History"),
                'view_mode': 'tree',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            raise UserError(_('You cannot access this field!!!!'))

    def action_hourly_cost(self):
        """This method checks the user's access rights and redirects to the
        'Hourly Cost Details'
        view if the user has the required access."""
        user_id = self.env['res.users'].browse(self._uid)
        if user_id.has_group('hr.group_hr_manager'):
            return {
                'name': _("Hourly Cost Details"),
                'view_mode': 'tree',
                'res_model': 'hourly.cost',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Hourly Cost Details"),
                'view_mode': 'tree',
                'res_model': 'hourly.cost',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError(_('You cannot access this field!!!!'))

    def action_salary_history(self):
        """This method checks the user's access rights and redirects to the
        'Salary History'
        view if the user has the required access."""
        user_id = self.env['res.users'].browse(self._uid)
        if user_id.has_group('hr.group_hr_manager'):
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError(_('You cannot access this field!!!!'))

    def action_contract_history(self):
        """This method checks the user's access rights and redirects to the
        'Contract History'
            view if the user has the required access."""
        user_id = self.env['res.users'].browse(self._uid)
        if user_id.has_group('hr.group_hr_manager'):
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee', '=', self.id)]
            }
        if self.id == self.env.user.employee_id.id:
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError(_('You cannot access this field!!!!'))
