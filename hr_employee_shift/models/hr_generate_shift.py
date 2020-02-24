# -*- coding: utf-8 -*-
from odoo import models, fields


class HrGenerateShift(models.Model):
    _name = 'hr.shift.generate'

    hr_department = fields.Many2one('hr.department', string="Department", help="Department")
    start_date = fields.Date(string="Start Date", required=True, help="Start date")
    end_date = fields.Date(string="End Date", required=True, help="End date")
    company_id = fields.Many2one('res.company', string='Company', help="Company")

    def action_schedule_shift(self):
        """Create mass schedule for all departments based on the shift scheduled in corresponding employee's contract"""

        if self.hr_department:
            for contract in self.env['hr.contract'].search([('department_id', '=', self.hr_department.id)]):
                if contract.shift_schedule:
                    for shift_val in contract.shift_schedule:
                        shift = shift_val.hr_shift
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search([('hr_department', '=', self.hr_department.id),
                                                                      ('name', '=', shift.name)], limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no), ('hr_department', '=', self.hr_department.id)], limit=1)
                    if new_shift:
                        shift_ids = [(0, 0, {
                                    'hr_shift': new_shift.id,
                                    'start_date': start_date,
                                    'end_date': end_date
                                })]
                        contract.shift_schedule = shift_ids
                    else:
                        seq_no = 1
                        new_shift = self.env['resource.calendar'].search([
                            ('sequence', '=', seq_no), ('hr_department', '=', self.hr_department.id)], limit=1)
                        if new_shift:
                            shift_ids = [(0, 0, {
                                'hr_shift': new_shift.id,
                                'start_date': start_date,
                                'end_date': end_date
                            })]
                            contract.shift_schedule = shift_ids
        else:
            for contract in self.env['hr.contract'].search([]):
                if contract.shift_schedule and contract.department_id:
                    for shift_val in contract.shift_schedule:
                        shift = shift_val.hr_shift
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search([('hr_department', '=', contract.department_id.id),
                                                                      ('name', '=', shift.name)], limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no), ('hr_department', '=', contract.department_id.id)], limit=1)
                    if new_shift:
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
                    else:
                        seq_no = 1
                        new_shift = self.env['resource.calendar'].search([
                            ('sequence', '=', seq_no), ('hr_department', '=', contract.department_id.id)], limit=1)
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids





