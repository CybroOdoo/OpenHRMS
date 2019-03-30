# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class DepartmentDetails(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('department_id')
    def _onchange_department(self):
        emp_id = self.env['hr.employee'].search([('id', '=', self._origin.id)])
        vals = {
            'emp_id': self._origin.id,
            'employee_name': emp_id.name,
            'updated_date': datetime.now(),
            'changed_field': 'Department',
            'current_value': self.department_id.name

        }
        self.env['department.history'].sudo().create(vals)

    @api.onchange('job_id')
    def onchange_job_id(self):
        emp_id = self.env['hr.employee'].search([('id', '=', self._origin.id)])
        vals = {
            'emp_id': self._origin.id,
            'employee_name': emp_id.name,
            'updated_date': datetime.today(),
            'changed_field': 'Job Position',
            'current_value': self.job_id.name

        }
        self.env['department.history'].sudo().create(vals)

    @api.onchange('timesheet_cost')
    def _onchange_timesheet_cost(self):
        emp_id = self.env['hr.employee'].search([('id', '=', self._origin.id)])
        vals = {
            'emp_id': self._origin.id,
            'employee_name': emp_id.name,
            'updated_date': datetime.now(),
            'current_value': self.timesheet_cost
        }
        self.env['timesheet.cost'].sudo().create(vals)

    @api.multi
    def department_details(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Department History"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('emp_id', '=', self.id)],
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Department History"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'department.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            raise UserError('You cannot access this field!!!!')

    @api.multi
    def time_sheet(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Timesheet Cost Details"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('emp_id', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Timesheet Cost Details"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'timesheet.cost',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError('You cannot access this field!!!!')

    @api.multi
    def salary_history(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('emp_id', '=', self.id)]
            }
        elif self.id == self.env.user.employee_id.id:
            return {
                'name': _("Salary History"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'salary.history',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            raise UserError('You cannot access this field!!!!')

    @api.multi
    def contract_history(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_manager'):
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'view_type': 'form',
                'res_model': 'contract.history',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': [('emp_id', '=', self.id)]
            }
        if self.id == self.env.user.employee_id.id:
            return {
                'name': _("Contract History"),
                'view_mode': 'tree',
                'view_type': 'form',
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
            'emp_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'current_value': self.wage,

        }
        self.env['salary.history'].sudo().create(vals)

    @api.onchange('name')
    def onchange_name(self):
        vals = {
            'emp_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'changed_field': 'Contract Reference',
            'current_value': self.name,

        }
        self.env['contract.history'].create(vals)

    @api.onchange('date_start')
    def onchange_datestart(self):
        vals = {
            'emp_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'changed_field': 'Start Date',
            'current_value': self.date_start,

        }
        self.env['contract.history'].create(vals)

    @api.onchange('date_end')
    def onchange_dateend(self):
        vals = {
            'emp_id': self.employee_id.id,
            'employee_name': self.employee_id,
            'updated_date': datetime.today(),
            'changed_field': 'End Date',
            'current_value': self.date_end,

        }
        self.env['contract.history'].create(vals)


class DepartmentHistory(models.Model):
    _name = 'department.history'

    emp_id = fields.Char(string='Employee Id')
    employee_name = fields.Char(string='Employee Name')
    changed_field = fields.Char(string='Changed Field')
    updated_date = fields.Date(string='Updated On')
    current_value = fields.Char(string='Current Value')


class TimesheetCost(models.Model):
    _name = 'timesheet.cost'

    emp_id = fields.Char(string='Employee Id')
    employee_name = fields.Char(string='Employee Name')
    updated_date = fields.Date(string='Updated On')
    current_value = fields.Char(string='Current Value')


class SalaryHistory(models.Model):
    _name = 'salary.history'

    emp_id = fields.Char(string='Employee Id')
    employee_name = fields.Char(string='Employee Name')
    updated_date = fields.Date(string='Updated On')
    current_value = fields.Char(string='Current Value')


class ContractHistory(models.Model):
    _name = 'contract.history'

    emp_id = fields.Char(string='Employee Id')
    employee_name = fields.Char(string='Employee Name')
    updated_date = fields.Date(string='Updated On')
    changed_field = fields.Char(string='Changed Field')
    current_value = fields.Char(string='Current Value')
