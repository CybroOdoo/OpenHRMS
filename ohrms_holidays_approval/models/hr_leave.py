# -*- coding: utf-8 -*-
################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    """Inherited to include more fields and functions"""
    _inherit = 'hr.leave'

    validation_status_ids = fields.One2many(
        'leave.validation.status',
        'leave_id',
        string='Leave Validators',
        track_visibility='always',
        help="Indicates the leave validators")
    multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        related='holiday_status_id.multi_level_validation',
        help="If checked then multi-level approval is necessary")
    user_id = fields.Many2one('res.users', string='User',
                              help='Current user',
                              default=lambda self: self.env.user)
    user_ids = fields.Many2many('res.users', string='Validators',
                                help='Leave validators',
                                compute="_compute_user_ids")

    @api.depends('validation_status_ids')
    def _compute_user_ids(self):
        """Method for computing user_ids"""
        for rec in self:
            rec.user_ids = rec.env['res.users'].search(
                [('id', 'in', rec.validation_status_ids.filtered(
                    lambda x: not x.validation_status).mapped('user_id').ids)])

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        """ Update the list view and add new validators
        when leave type is changed in leave request form """
        li = []
        self.validation_status_ids = [(5, 0, 0)]
        li2 = []
        for user in self.validation_status_ids:
            li2.append(user.user_id.id)
        for user in self.holiday_status_id.validator_ids.filtered(
                lambda x: x.user_id.id not in li2):
            li.append((0, 0, {
                'user_id': user.user_id.id,
            }))
        self.validation_status_ids = li

    def action_approve(self):
        """ Override action_approve to add multi level approval """
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_(
                'Leave request must be confirmed ("To Approve")'
                ' in order to approve it.'))
        return self.approval_check()

    def approval_check(self):
        """ Override to check all leave validators approved the leave request
            if approved change the current request stage to Approved"""
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        active_id = self.env.context.get('active_id') if self.env.context.get(
            'active_id') else self.id
        user = self.env['hr.leave'].browse(active_id)
        if self.env.uid in user.validation_status_ids.mapped('user_id').ids:
            user.validation_status_ids.search(
                [('leave_id', '=', user.id),
                 ('user_id', '=', self.env.uid)]).validation_status = True
        approval_flag = True
        for user_obj in user.validation_status_ids:
            if not user_obj.validation_status:
                approval_flag = False
        if approval_flag:
            user.filtered(
                lambda hol: hol.validation_type == 'both').sudo().write(
                {'state': 'validate1',
                 'first_approver_id': current_employee.id})
            user.filtered(
                lambda hol:
                not hol.validation_type == 'both').sudo().action_validate()
            if not user.env.context.get('leave_fast_create'):
                user.activity_update()
            self.user_ids = [(4, 0, self.env.uid)]
            return True
        return False

    def action_refuse(self):
        """ Override to refuse the leave request if the current user is in
        validators list """
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        approval_access = False
        for user in self.validation_status_ids:
            if user.user_id.id == self.env.uid:
                approval_access = True
        if approval_access:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))
                if holiday.state == 'validate1':
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'first_approver_id': current_employee.id})
                else:
                    holiday.sudo().write(
                        {'state': 'refuse',
                         'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
            self._remove_resource_leave()
            self.activity_update()
            validation_obj = self.validation_status_ids.search(
                [('leave_id', '=', self.id),
                 ('user_id', '=', self.env.uid)])
            validation_obj.validation_status = False
            return True
        else:
            for holiday in self:
                if holiday.state not in ['confirm', 'validate', 'validate1']:
                    raise UserError(_(
                        'Leave request must be confirmed '
                        'or validated in order to refuse it.'))
                if holiday.state == 'validate1':
                    holiday.write({'state': 'refuse',
                                   'first_approver_id': current_employee.id})
                else:
                    holiday.write({'state': 'refuse',
                                   'second_approver_id': current_employee.id})
                # Delete the meeting
                if holiday.meeting_id:
                    holiday.meeting_id.unlink()
            self._remove_resource_leave()
            self.activity_update()
            return True

    def action_draft(self):
        """ Reset all validation status to false when leave request
        set to draft stage"""
        for user in self.validation_status_ids:
            user.validation_status = False
        return super().action_draft()

    def _get_approval_requests(self):
        """ Action for Approvals menu item to show approval
        requests assigned to current user """
        current_uid = self.env.uid
        hr_holidays = self.env['hr.leave'].search([('state', '=', 'confirm')])
        li = []
        for req in hr_holidays:
            if any(val_status.user_id.id == current_uid for val_status in
                   req.validation_status_ids):
                li.append(req.id)
        value = {
            'domain': str([('id', 'in', li)]),
            'view_mode': 'list,form',
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
