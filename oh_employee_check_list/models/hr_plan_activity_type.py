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
from odoo import fields, models, _
from odoo.exceptions import UserError


class HrPlanActivityType(models.Model):
    """Inherit hr_plan_activity_type for adding entry and exit checklist plan"""
    _inherit = 'hr.plan.activity.type'

    entry_plan_activity_ids = fields.Many2many('employee.checklist',
                                               'entry_plan_ids',
                                               'check_hr_rel',
                                               'hr_check_rel',
                                               string='Entry Process',
                                               domain=[('document_type', '=',
                                                        'entry')],
                                               help="Choose Entry Plan")
    exit_plan_activity_ids = fields.Many2many('employee.checklist',
                                              'exit_plan_ids',
                                              'exit_hr_rel',
                                              'hr_exit_rel',
                                              string='Exit Process',
                                              domain=[
                                                  ('document_type', '=',
                                                   'exit')],
                                              help="Choose Exit Plan")

    def unlink(self):
        """
        Function is used for while deleting the planing types
        it check if the record is related to checklist and raise
        error.
        """
        if self.plan_id == self.env.ref('hr.onboarding_plan'):
            check_id = self.env.ref(
                'oh_employee_check_list.checklist_onboarding_activity_type')
        else:
            check_id = self.env.ref(
                'oh_employee_check_list.checklist_offboarding_activity_type')
        for recd in self:
            if recd.id == check_id.id:
                raise UserError(_("Checklist Record Can't Be Delete!"))
        return super(HrPlanActivityType, self).unlink()
