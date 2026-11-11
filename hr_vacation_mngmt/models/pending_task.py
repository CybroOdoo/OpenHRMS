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


class PendingTask(models.Model):
    """ Model for Pending Tasks associated with HR Leave Requests."""
    _name = 'pending.task'
    _description = 'Pending Task'

    name = fields.Char(string='Task', required=True,
                       help='Name of the pending task.')
    leave_id = fields.Many2one('hr.leave', string='Leave Request',
                               help="Leave request of the employee.")
    dept_id = fields.Many2one('hr.department', string='Department',
                              related='leave_id.department_id',
                              help="Department of the employee.")
    project_id = fields.Many2one('project.project',
                                 string='Project',required=True,
                                 help="Project of the employee")
    description = fields.Text(string='Description',
                              help="Description of the task.")
    assigned_person_id = fields.Many2one('hr.employee',
                                         string='Assigned to',
                                         help="Employee who is assigned to",
                                         domain="[('department_id', '=', "
                                                "dept_id)]")
    unavailable_employee_ids = fields.Many2many('hr.employee',
                                                string='Unavailable Employees',
                                                help="Name of unavailable"
                                                     "employees",
                                                compute='_compute_unavailable_employee_ids')

    @api.depends('leave_id')
    def _compute_unavailable_employee_ids(self):
        """Compute method to determine employees with overlapping leaves."""
        for task in self:
            task.unavailable_employee_ids = task.leave_id.overlapping_leaves_ids.employee_id
