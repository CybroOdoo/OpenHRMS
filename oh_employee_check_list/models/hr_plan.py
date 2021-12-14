from odoo import models, fields, _
from odoo.exceptions import UserError


class HrPlanActivityTypeChecklist(models.Model):
    _inherit = 'hr.plan.activity.type'

    entry_checklist_plan = fields.Many2many('employee.checklist', 'entry_obj_plan', 'check_hr_rel', 'hr_check_rel',
                                            string='Entry Process',
                                            domain=[('document_type', '=', 'entry')])
    exit_checklist_plan = fields.Many2many('employee.checklist', 'exit_obj_plan', 'exit_hr_rel', 'hr_exit_rel',
                                           string='Exit Process',
                                           domain=[('document_type', '=', 'exit')])

    def unlink(self):
        """
        Function is used for while deleting the planing types
        it check if the record is related to checklist and raise
        error.

        """
        check_id = self.env.ref('oh_employee_check_list.checklist_activity_type')
        for recd in self:
            if recd.id == check_id.id:
                raise UserError(_("Checklist Record Can't Be Delete!"))
        return super(HrPlanActivityTypeChecklist, self).unlink()


class EmployeeChecklistInherit(models.Model):
    _inherit = 'employee.checklist'

    entry_obj_plan = fields.Many2many('hr.employee', 'entry_checklist_plan', 'hr_check_rel', 'check_hr_rel',
                                      invisible=1)
    exit_obj_plan = fields.Many2many('hr.employee', 'exit_checklist_plan', 'hr_exit_rel', 'exit_hr_rel',
                                     invisible=1)


class MailActivityChecklist(models.Model):
    _inherit = 'mail.activity'

    entry_checklist_plan = fields.Many2many('employee.checklist', 'check_hr_rel', 'hr_check_rel',
                                            string='Entry Process',
                                            domain=[('document_type', '=', 'entry')], help="Entry Checklist's")
    exit_checklist_plan = fields.Many2many('employee.checklist', 'exit_hr_rel', 'hr_exit_rel',
                                           string='Exit Process',
                                           domain=[('document_type', '=', 'exit')], help="Exit Checklists's")
    check_type_check = fields.Boolean()
    on_board_type_check = fields.Boolean()
    off_board_type_check = fields.Boolean()

    def action_close_dialog(self):
        """
        Function is used for writing checklist values based on
        mail activity of the employee.
        """
        emp_checklist = self.env['hr.employee'].search([('id', '=', self.res_id)])
        emp_checklist.write({
            'entry_checklist': self.entry_checklist_plan if self.entry_checklist_plan else emp_checklist.entry_checklist,
            'exit_checklist': self.exit_checklist_plan if self.exit_checklist_plan else emp_checklist.exit_checklist
        })

        return super(MailActivityChecklist, self).action_close_dialog()


class HrPlanWizardInherited(models.TransientModel):
    _inherit = 'hr.plan.wizard'

    def action_launch(self):
        """
        Function is override for appending checklist values
        to the mail activity.

        """
        check_type_id = self.env.ref('oh_employee_check_list.checklist_activity_type')
        on_id = self.env.ref('hr.onboarding_plan')
        of_id = self.env.ref('hr.offboarding_plan')
        for activity_type in self.plan_id.plan_activity_type_ids:
            responsible = activity_type.get_responsible_id(self.employee_id)

            if self.env['hr.employee'].with_user(responsible).check_access_rights('read', raise_exception=False):
                self.env['mail.activity'].create({
                    'res_id': self.employee_id.id,
                    'res_model_id': self.env['ir.model']._get('hr.employee').id,
                    'summary': activity_type.summary,
                    'note': activity_type.note,
                    'activity_type_id': activity_type.activity_type_id.id,
                    'user_id': responsible.id,
                    'entry_checklist_plan': activity_type.entry_checklist_plan,
                    'exit_checklist_plan': activity_type.exit_checklist_plan,
                    'check_type_check': True if activity_type.id == check_type_id.id else False,
                    'on_board_type_check': True if self.plan_id.id == on_id.id else False,
                    'off_board_type_check': True if self.plan_id.id == of_id.id else False
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'name': self.employee_id.display_name,
            'view_mode': 'form',
            'views': [(False, "form")],
        }


class HrPlanCheckList(models.Model):
    _inherit = 'hr.plan'

    def unlink(self):
        """
        Function is used for checking while deleting
        plan which is related to checklist record
        and raise error.

        """
        on_id = self.env.ref('hr.onboarding_plan')
        of_id = self.env.ref('hr.offboarding_plan')
        for recd in self:
            if recd.id == of_id.id or recd.id == on_id.id:
                raise UserError(_("Checklist Record's Can't Be Delete!"))
        return super(HrPlanCheckList, self).unlink()
