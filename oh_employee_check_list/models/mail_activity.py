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


class MailActivity(models.Model):
    """Inherit mail_activity model for adding Entry and Exit Processes"""
    _inherit = 'mail.activity'

    entry_plan_activity_ids = fields.Many2many('employee.checklist',
                                               'check_hr_rel',
                                               'hr_check_rel',
                                               string='Entry Process',
                                               domain=[('document_type', '=',
                                                        'entry')],
                                               help="Choose Entry Checklist")
    exit_plan_activity_ids = fields.Many2many('employee.checklist',
                                              'exit_hr_rel',
                                              'hr_exit_rel',
                                              string='Exit Process',
                                              domain=[
                                                  ('document_type', '=',
                                                   'exit')],
                                              help="Choose Exit Checklist")
    check_type_check = fields.Boolean(string="Checklist Type",
                                      help="Checks Checklist type"
                                           "and Activity type is same")
    on_board_type_check = fields.Boolean(string="On Board Checklist Type",
                                         help="Checks Plan and Onboard Plan"
                                              "is same")
    off_board_type_check = fields.Boolean(string="OFF Board Checklist Type",
                                          help="Checks Plan and Offboard Plan"
                                               "is same")

    def action_close_dialog(self):
        """
        Function is used for writing checklist values based on
        mail activity of the employee.
        """
        employee_checklist = self.env['hr.employee'].search(
            [('id', '=', self.res_id)])
        employee_checklist.write({
            'employee_entry_checklist_ids': self.entry_plan_activity_ids if self.entry_plan_activity_ids else employee_checklist.employee_entry_checklist_ids,
            'employee_exit_checklist_ids': self.exit_plan_activity_ids if self.exit_plan_activity_ids else employee_checklist.employee_exit_checklist_ids
        })
        return super(MailActivity, self).action_close_dialog()
