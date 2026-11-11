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
from odoo import fields, models


class HrTraining(models.Model):
    """Model to manage employee training, particularly probation periods.
        This class tracks the start and end dates of the probation period,
        the state of training (new or extended), and any associated leaves
        taken during the probation period."""
    _name = 'hr.training'
    _rec_name = 'employee_id'
    _description = 'HR Training'

    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  help="Select the employee")
    start_date = fields.Date(string="Start Date",
                             help="Probation starting date")
    end_date = fields.Date(string="End Date", help="Probation end date")
    state = fields.Selection(
        [('new', 'New'), ('extended', 'Extended')], required=True,
        default='new', help="State of the training.")
    leave_ids = fields.Many2many('hr.leave', string="Leave",
                                 help="Leave in the period of training.")
