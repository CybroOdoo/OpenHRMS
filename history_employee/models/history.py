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
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class DepartmentDetails(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('department_id')
    def _onchange_department(self):
        employee_id = self.env['hr.employee'].search([('id', '=', self._origin.id)])
        vals = {
            'employee_id': self._origin.id,
            'employee_name': employee_id.name,
            'updated_date': datetime.now(),
            'changed_field': 'Department',
            'current_value': self.department_id.name

        }
        self.env['department.history'].sudo().create(vals)

    @api.onchange('job_id')
    def onchange_job_id(self):
        employee_id = self.env['hr.employee'].search([('id', '=', self._origin.id)])
        vals = {
            'employee_id': self._origin.id,
            'employee_name': employee_id.name,
            'updated_date': datetime.today(),
            'changed_field': 'Job Position',
            'current_value': self.job_id.name

        }
        self.env['department.history'].sudo().create(vals)

    @api.onchange('timesheet_cost')
    def _onchange_timesheet_cost(self):
        employee_id = self.env['hr.employee'].search([('id', '=', self._origin.id)])
        vals = {
            'employee_id': self._origin.id,
            'employee_name': employee_id.name,
            'updated_date': datetime.now(),
            'current_value': self.timesheet_cost
        }
        self.env['timesheet.cost'].sudo().create(vals)

    def department_details(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Department History"),
                'view_mode': 'tree',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)],
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Department History"),
                'view_mode': 'tree',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            raise UserError('You cannot access this field!!!!')

    def time_sheet(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Timesheet Cost Details"),
                'view_mode': 'tree',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Timesheet Cost Details"),
                'view_mode': 'tree',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError('You cannot access this field!!!!')

    def salary_history(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)]
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
            raise UserError('You cannot access this field!!!!')

    def contract_history(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('employee_id', '=', self.id)]
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
            raise UserError('You cannot access this field!!!!')


class WageDetails(models.Model):
    _inherit = 'hr.contract'

    @api.onchange('wage')
    def onchange_wage(self):
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'current_value': self.wage,

        }
        self.env['salary.history'].sudo().create(vals)

    @api.onchange('name')
    def onchange_name(self):
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'changed_field': 'Contract Reference',
            'current_value': self.name,

        }
        self.env['contract.history'].create(vals)

    @api.onchange('date_start')
    def onchange_datestart(self):
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'changed_field': 'Start Date',
            'current_value': self.date_start,

        }
        self.env['contract.history'].create(vals)

    @api.onchange('date_end')
    def onchange_dateend(self):
        vals = {
            'employee_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'changed_field': 'End Date',
            'current_value': self.date_end,

        }
        self.env['contract.history'].create(vals)


class DepartmentHistory(models.Model):
    _name = 'department.history'

    employee_id = fields.Char(string='Employee Id', help="Employee")
    employee_name = fields.Char(string='Employee Name', help="Name")
    changed_field = fields.Char(string='Job position', help="Displays the changed department/job position")
    updated_date = fields.Date(string='Date', help="Display the date on which  department or job position changed")
    current_value = fields.Char(string='Designation', help="Display the designation")


class TimesheetCost(models.Model):
    _name = 'timesheet.cost'

    employee_id = fields.Char(string='Employee Id', help="Employee")
    employee_name = fields.Char(string='Employee Name', help="Name")
    updated_date = fields.Date(string='Updated On', help="Updated Date of Time Sheet")
    current_value = fields.Char(string='Current Cost', help="Updated Value of Time Sheet")


class SalaryHistory(models.Model):
    _name = 'salary.history'

    employee_id = fields.Char(string='Employee Id', help="Employee")
    employee_name = fields.Char(string='Employee Name', help="Name")
    updated_date = fields.Date(string='Updated On', help="Salary Updated Date")
    current_value = fields.Char(string='Current Salary', help="Updated Salary")


class ContractHistory(models.Model):
    _name = 'contract.history'

    employee_id = fields.Char(string='Employee Id', help="Employee")
    employee_name = fields.Char(string='Employee Name', help="Name")
    updated_date = fields.Date(string='Updated On', help="Contract Updated Date")
    changed_field = fields.Char(string='Changed Field', help="Updated Field's")
    current_value = fields.Char(string='Current Contract', help="Updated Value of Contract")
