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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrPayslipEmployeeLine(models.TransientModel):
    """Wizard line to select individual employees for payslip generation."""
    _name = 'hr.payslip.employee.line'
    _description = 'Payslip Employee Line'

    wizard_id = fields.Many2one('hr.payslip.employees')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    is_selected = fields.Boolean(string='Select', default=False)
    job_id = fields.Many2one(related='employee_id.job_id', string='Job')
    department_id = fields.Many2one(related='employee_id.department_id', string='Department')


class HrPayslipEmployees(models.TransientModel):
    """Create new model for Generate payslips for all selected employees"""
    _name = 'hr.payslip.employees'
    _description = 'Generate Payslips for All Selected Employees'

    line_ids = fields.One2many('hr.payslip.employee.line', 'wizard_id', string='Employee Lines')
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batch')
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', string='Employees', help="Choose employee for Payslip")
    structure_id = fields.Many2one('hr.payroll.structure', string='Structure')

    @api.model
    def default_get(self, fields):
        """Populate the default employees and structure based on the current context."""
        res = super(HrPayslipEmployees, self).default_get(fields)

        active_id = self.env.context.get('batch_run_id') or self.env.context.get('active_id')
        struct_id = self.env.context.get('default_struct_id')

        if active_id:
            run = self.env['hr.payslip.run'].browse(active_id)

            # Base domain: Employee must have an active contract during the run dates
            domain = [
                ('date_start', '<=', run.date_end),
                '|', ('date_end', '>=', run.date_start), ('date_end', '=', False),
            ]

            # If a structure is provided, ADD the structure condition to the domain
            if struct_id:
                domain += ['|', ('struct_id', '=', struct_id), ('structure_type_id.default_struct_id', '=', struct_id)]
                res['structure_id'] = struct_id

            # Search contracts and create the un-ticked checkbox lines
            contracts = self.env['hr.version'].search(domain)
            lines = []
            for emp in contracts.mapped('employee_id'):
                lines.append((0, 0, {
                    'employee_id': emp.id,
                    'is_selected': False,
                }))

            res['line_ids'] = lines
            res['payslip_run_id'] = active_id

        return res

    def action_compute_sheet(self):
        """Function for compute Payslip Sheet"""
        payslips = self.env['hr.payslip']
        
        # In standard flow, active_id is the batch
        active_id = self.payslip_run_id.id if self.payslip_run_id else self.env.context.get('active_id')
        if active_id:
            run_data = self.env['hr.payslip.run'].browse(active_id)
            from_date = run_data.date_start
            to_date = run_data.date_end
            credit_note = run_data.credit_note
        else:
            raise UserError(_("No Payslip Batch associated. Please restart the process from the Payslip Batch form."))
        # If structure is set, use the new checkboxes logic. Otherwise, use the standard many2many field.
        selected_lines = self.line_ids.filtered(lambda l: l.is_selected)
        employees = selected_lines.mapped('employee_id')

        for employee in employees:
            slip_data = self.env['hr.payslip'].onchange_employee_id(
                from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', [])],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', [])],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'company_id': employee.company_id.id,
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.action_compute_sheet()
        return {'type': 'ir.actions.act_window_close'}