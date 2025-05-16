# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import fields, models


class HrGenerateShift(models.Model):
    """This class is responsible for generating shift schedules for employees
        based on the shifts defined in their respective contracts. The generated
        shifts can be for specific departments or for all departments if no
        specific department is selected. """
    _name = 'hr.shift.generate'
    _description = 'Generating shift schedules for employees'

    hr_department = fields.Many2one('hr.department',
                                    string="Department", help="Department of employee")
    start_date = fields.Date(string="Start Date", required=True,
                             help="Start date of the shift")
    end_date = fields.Date(string="End Date", required=True, help="End date of shift")
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Company related to this shift")

    def action_schedule_shift(self):
        """Create mass schedule for all departments based on the shift
         scheduled in corresponding employee's contract"""
        if self.hr_department:
            for contract in self.env['hr.contract'].search(
                    [('department_id', '=', self.hr_department.id)]):
                if contract.shift_schedule:
                    for shift_val in contract.shift_schedule:
                        shift = shift_val.hr_shift
                    start_date = self.start_date
                    end_date = self.end_date
                    shift_obj = self.env['resource.calendar'].search(
                        [('hr_department', '=', self.hr_department.id),
                         ('name', '=', shift.name)], limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no),
                        ('hr_department', '=', self.hr_department.id)], limit=1)
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
                            ('sequence', '=', seq_no),
                            ('hr_department', '=', self.hr_department.id)],
                            limit=1)
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
                    shift_obj = self.env['resource.calendar'].search(
                        [('hr_department', '=', contract.department_id.id),
                         ('name', '=', shift.name)], limit=1)
                    sequence = shift_obj.sequence
                    seq_no = sequence + 1
                    new_shift = self.env['resource.calendar'].search([
                        ('sequence', '=', seq_no),
                        ('hr_department', '=', contract.department_id.id)],
                        limit=1)
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
                            ('sequence', '=', seq_no),
                            ('hr_department', '=', contract.department_id.id)],
                            limit=1)
                        shift_ids = [(0, 0, {
                            'hr_shift': new_shift.id,
                            'start_date': start_date,
                            'end_date': end_date
                        })]
                        contract.shift_schedule = shift_ids
