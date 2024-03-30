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
from odoo import models


class HrPlanWizard(models.TransientModel):
    """Inherit hr_plan_wizard model for super action_launch button"""
    _inherit = 'hr.plan.wizard'

    def action_launch(self):
        """
        Function is override for appending checklist values
        to the mail activity.
        """
        if self.plan_id == self.env.ref('hr.onboarding_plan'):
            check_type_id = self.env.ref(
                'oh_employee_check_list.checklist_onboarding_activity_type')
        else:
            check_type_id = self.env.ref(
                'oh_employee_check_list.checklist_offboarding_activity_type')
        onboard_id = self.env.ref('hr.onboarding_plan')
        offboard_id = self.env.ref('hr.offboarding_plan')
        for activity_type in self.plan_id.plan_activity_type_ids:
            responsible = activity_type.get_responsible_id(self.employee_ids)[
                'responsible']
            if self.env['hr.employee'].with_user(
                    responsible).check_access_rights('read',
                                                     raise_exception=False):
                self.env['mail.activity'].create({
                    'res_id': self.employee_ids.id,
                    'res_model_id': self.env['ir.model']._get('hr.employee').id,
                    'summary': activity_type.summary,
                    'note': activity_type.note,
                    'activity_type_id': activity_type.activity_type_id.id,
                    'user_id': responsible.id,
                    'entry_plan_activity_ids': activity_type.entry_plan_activity_ids,
                    'exit_plan_activity_ids': activity_type.exit_plan_activity_ids,
                    'check_type_check': True if activity_type.id == check_type_id.id else False,
                    'on_board_type_check': True if self.plan_id.id == onboard_id.id else False,
                    'off_board_type_check': True if self.plan_id.id == offboard_id.id else False
                })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_ids.id,
            'name': self.employee_ids.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }
