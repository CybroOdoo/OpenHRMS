# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import email_split


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    leave_approvals = fields.One2many('leave.validation.status',
                                      'holiday_status',
                                      string='Leave Validators',
                                      track_visibility='always', help="Leave approvals")
    multi_level_validation = fields.Boolean(string='Multiple Level Approval',
                                            related='holiday_status_id.multi_level_validation',
                                            help="If checked then multi-level approval is necessary")


    def action_approve(self):
        """ Chack if any pending tasks is added if so reassign the pending
        task else call approval """
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_(
                'Leave request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        ohrmspro_vacation_project = self.sudo().env['ir.module.module'].search(
            [('name', '=', 'ohrmspro_vacation_project')],
            limit=1).state

        if ohrmspro_vacation_project == 'installed':
            return self.env['hr.leave'].check_pending_task(self)
        else:
            return self.approval_check()

    def approval_check(self):
        """ Check all leave validators approved the leave request if approved
         change the current request stage to Approved"""

        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        li = []
        if self.env.context.get('active_id'):
            active_id = self.env.context.get('active_id')
        else:
            active_id = self.id
        user = self.env['hr.leave'].search([('id', '=', active_id)], limit=1)
        for user_obj in user.leave_approvals:
            li.append(user_obj.validating_users.id)
        if self.env.uid in li:
            validation_obj = user.leave_approvals.search(
                [('holiday_status', '=', user.id),
                 ('validating_users', '=', self.env.uid)])
            validation_obj.validation_status = True
        approval_flag = True
        for user_obj in user.leave_approvals:
            if not user_obj.validation_status:
                approval_flag = False
        if approval_flag:
            user.filtered(
                lambda hol: hol.validation_type == 'both').sudo().write(
                {'state': 'validate1',
                 'first_approver_id': current_employee.id})
            user.filtered(lambda
                              hol: not hol.validation_type == 'both').sudo().action_validate()
            if not user.env.context.get('leave_fast_create'):
                user.activity_update()
            return True
        else:
            return False

    def action_refuse(self):
        """ Refuse the leave request if the current user is in
        validators list """
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

        approval_access = False
        for user in self.leave_approvals:
            if user.validating_users.id == self.env.uid:
                approval_access = True
        if approval_access:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed or validated in order to refuse it.'))

                if holiday.state == 'validate1':
                    holiday.sudo().write({'state': 'refuse',
                                          'first_approver_id': current_employee.id})
                else:
                    holiday.sudo().write({'state': 'refuse',
                                          'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # If a category that created several holidays, cancel all related
                holiday.linked_request_ids.action_refuse()
            self._remove_resource_leave()
            self.activity_update()
            validation_obj = self.leave_approvals.search(
                [('holiday_status', '=', self.id),
                 ('validating_users', '=', self.env.uid)])
            validation_obj.validation_status = False
            return True
        else:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed or validated in order to refuse it.'))

                if holiday.state == 'validate1':
                    holiday.write({'state': 'refuse',
                                   'first_approver_id': current_employee.id})
                else:
                    holiday.write({'state': 'refuse',
                                   'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
                # If a category that created several holidays, cancel all related
                holiday.linked_request_ids.action_refuse()
            self._remove_resource_leave()
            self.activity_update()
            return True

    def action_draft(self):
        """ Reset all validation status to false when leave request
        set to draft stage"""
        for user in self.leave_approvals:
            user.validation_status = False
        return super(HrLeave, self).action_draft()

    @api.onchange('holiday_status_id')
    def add_validators(self):
        """ Update the tree view and add new validators
        when leave type is changed in leave request form """

        li = []
        self.leave_approvals = [(5, 0, 0)]
        li2 = []
        for user in self.leave_approvals:
            li2.append(user.validating_users.id)
        for l in self.holiday_status_id.leave_validators:
            if l.holiday_validators.id not in li2:
                li.append((0, 0, {
                    'validating_users': l.holiday_validators.id,
                }))
        self.leave_approvals = li

    def _get_approval_requests(self):
        """ Action for Approvals menu item to show approval
        requests assigned to current user """

        current_uid = self.env.uid
        hr_holidays = self.env['hr.leave'].search([])
        li = []
        for l in hr_holidays:
            if l.state == 'confirm':
                for user in l.leave_approvals:
                    if user.validating_users.id == current_uid:
                        li.append(l.id)
        value = {
            'domain': str([('id', 'in', li)]),
            'view_mode': 'tree,form',
            'res_model': 'hr.leave',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'name': _('Approvals'),
            'res_id': self.id,
            'target': 'current',
            'create': False,
            'edit': False,
        }
        return value


class HrLeaveTypes(models.Model):
    """ Extend model to add multilevel approval """
    _inherit = 'hr.leave.type'

    multi_level_validation = fields.Boolean(string='Multiple Level Approval',
                                            help="If checked then multi-level approval is necessary")
    validation_type = fields.Selection(selection_add=[('multi', 'Multi Level Approval')])
    leave_validators = fields.One2many('hr.holidays.validators',
                                       'hr_holiday_status',
                                       string='Leave Validators', help="Leave validators")

    @api.onchange('validation_type')
    def enable_multi_level_validation(self):
        """ Enabling the boolean field of multilevel validation"""
        if self.validation_type == 'multi':
            self.multi_level_validation = True
        else:
            self.multi_level_validation = False

    @api.onchange('multi_level_validation')
    def disable_double_validation(self):
        """ Disable doy=uble validation when multi level a
        pproval is disabled """
        if self.multi_level_validation:
            self.double_validation = False

    @api.onchange('double_validation')
    def disable_multi_approval(self):
        """ Disable multi level approval when double validation is enabled """
        if self.double_validation:
            self.multi_level_validation = False


class HrLeaveValidators(models.Model):
    """ Model for leave validators in Leave Types configuration """
    _name = 'hr.holidays.validators'

    hr_holiday_status = fields.Many2one('hr.leave.type')

    holiday_validators = fields.Many2one('res.users',
                                         string='Leave Validators', help="Leave validators",
                                         domain="[('share','=',False)]")


class LeaveValidationStatus(models.Model):
    """ Model for leave validators and their status for each leave request """
    _name = 'leave.validation.status'

    holiday_status = fields.Many2one('hr.leave')

    validating_users = fields.Many2one('res.users', string='Leave Validators', help="Leave validators",
                                       domain="[('share','=',False)]")
    validation_status = fields.Boolean(string='Approve Status', readonly=True,
                                       default=False,
                                       track_visibility='always', help="Status")
    leave_comments = fields.Text(string='Comments', help="Comments")

    @api.onchange('validating_users')
    def prevent_change(self):
        """ Prevent Changing leave validators from leave request form """
        raise UserError(_(
            "Changing leave validators is not permitted. You can only change "
            "it from Leave Types Configuration"))
