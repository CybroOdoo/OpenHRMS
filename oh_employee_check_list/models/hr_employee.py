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
from odoo import api, fields, models


class HrEmployee(models.Model):
    """Inherit hr_employee model for getting percentage of
    Entry and Exit processes"""
    _inherit = 'hr.employee'

    employee_entry_checklist_ids = fields.Many2many('employee.checklist',
                                                    'checklist_entry_ids',
                                                    'check_hr_rel',
                                                    'hr_check_rel',
                                                    string='Entry Process',
                                                    domain=[('document_type',
                                                             '=', 'entry')],
                                                    help="Entry Checklist" 
                                                         "for Employee")
    employee_exit_checklist_ids = fields.Many2many('employee.checklist',
                                                   'checklist_exit_ids',
                                                   'exit_hr_rel',
                                                   'hr_exit_rel',
                                                   string='Exit Process',
                                                   domain=[(
                                                           'document_type', '=',
                                                           'exit')],
                                                   help="Exit Checklists" 
                                                        "for Employee")
    entry_progress = fields.Float(string='Entry Progress',
                                  compute='_compute_entry_progress',
                                  default=0.0,
                                  help="Percentage of Entry Checklist")
    exit_progress = fields.Float(string='Exit Progress',
                                 compute='_compute_exit_progress',
                                 default=0.0,
                                 help="Percentage of Exit Checklist")
    maximum_rate = fields.Integer(string="Rate", default=100,
                                  help="Maximum Rate of Entry"
                                       "and Exit Progress")
    check_list_enable = fields.Boolean(string="Is Check List", invisible=True,
                                       copy=False,
                                       help="When enabling Entry and Exit"
                                            "details will shows under"
                                            "Checklist")

    @api.depends('employee_exit_checklist_ids')
    def _compute_exit_progress(self):
        """Function for getting count of total Exit Processes"""
        for each in self:
            total_length = self.env['employee.checklist'].search_count(
                [('document_type', '=', 'exit')])
            entry_length = len(each.employee_exit_checklist_ids)
            if total_length != 0:
                each.exit_progress = (entry_length * 100) / total_length

    @api.depends('employee_entry_checklist_ids')
    def _compute_entry_progress(self):
        """Function for getting count of total Entry Processes"""
        for each in self:
            total_length = self.env['employee.checklist'].search_count(
                [('document_type', '=', 'entry')])
            entry_length = len(each.employee_entry_checklist_ids)
            if total_length != 0:
                each.entry_progress = (entry_length * 100) / total_length
