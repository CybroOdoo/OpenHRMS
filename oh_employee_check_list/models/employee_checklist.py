# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models


class EmployeeChecklist(models.Model):
    """Create new model for employee_checklist where can see
    all Entry and Exit Processes"""
    _name = 'employee.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"
    _order = 'sequence'

    name = fields.Char(string='Name', copy=False, required=1,
                       help="Checklist Name for Employee")
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')],
                                     string='Checklist Type',
                                     help='Type of Checklist for Employee',
                                     required=1)
    sequence = fields.Integer(string='Sequence', help="Sequence for Checklist")
    checklist_entry_ids = fields.Many2many('hr.employee',
                                           'employee_entry_checklist_ids',
                                           'hr_check_rel',
                                           'check_hr_rel',
                                           string="Entry Process",
                                           help="Employee Entry Process" 
                                                "for Checklist",
                                           invisible=1)
    checklist_exit_ids = fields.Many2many('hr.employee',
                                          'employee_exit_checklist_ids',
                                          'hr_exit_rel',
                                          'exit_hr_rel',
                                          string="Exit Process",
                                          help="Employee Exit Process" 
                                               "for Checklist",
                                          invisible=1)
    entry_plan_ids = fields.Many2many('hr.employee',
                                      'entry_plan_activity_ids',
                                      'hr_check_rel',
                                      'check_hr_rel',
                                      string="Entry Plan Process",
                                      help="Employee Entry Plan Process"
                                           "for Checklist",
                                      invisible=1)
    exit_plan_ids = fields.Many2many('hr.employee',
                                     'exit_plan_activity_ids',
                                     'hr_exit_rel',
                                     'exit_hr_rel',
                                     string="Exit PLan Process",
                                     help="Employee Exit Plan for Checklist",
                                     invisible=1)
