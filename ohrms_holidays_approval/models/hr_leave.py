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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    """Inherited to include multi-level validation functions in Odoo 20"""
    _inherit = 'hr.leave'

    validation_status_ids = fields.One2many(
        'leave.validation.status',
        'leave_id',
        string='Leave Validators',
        help="Indicates the leave validators")
    multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        related='work_entry_type_id.multi_level_validation',
        store=True,
        help="If checked then multi-level approval is necessary")
    user_ids = fields.Many2many(
        'res.users',
        string='Validators',
        help='Leave validators awaiting approval',
        compute="_compute_user_ids")

    @api.depends('validation_status_ids.validation_status', 'validation_status_ids.user_id')
    def _compute_user_ids(self):
        """Method for computing user_ids awaiting approval"""
        for rec in self:
            rec.user_ids = rec.validation_status_ids.filtered(
                lambda x: not x.validation_status
            ).mapped('user_id')

    @api.onchange('work_entry_type_id')
    def _onchange_work_entry_type_id(self):
        """Update validators when work entry type is changed in leave request form"""
        if self.work_entry_type_id and self.work_entry_type_id.multi_level_validation:
            self.validation_status_ids = [(5, 0, 0)] + [
                (0, 0, {
                    'user_id': validator.user_id.id,
                    'validation_status': False,
                })
                for validator in self.work_entry_type_id.validator_ids
            ]
        else:
            self.validation_status_ids = [(5, 0, 0)]

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to populate initial validation status records."""
        for vals in vals_list:
            work_entry_type_id = vals.get('work_entry_type_id')
            if work_entry_type_id and not vals.get('validation_status_ids'):
                wet = self.env['hr.work.entry.type'].browse(work_entry_type_id)
                if wet.multi_level_validation and wet.validator_ids:
                    vals['validation_status_ids'] = [
                        (0, 0, {
                            'user_id': v.user_id.id,
                            'validation_status': False,
                        }) for v in wet.validator_ids
                    ]
        records = super(HrLeave, self.with_context(leave_multi_create=True)).create(vals_list)
        return records.with_context(leave_multi_create=False)

    @api.depends_context('uid')
    @api.depends('state', 'employee_id', 'department_id', 'multi_level_validation', 'user_ids')
    def _compute_can_approve(self):
        """Compute whether the current user can approve the multi-level leave request."""
        super()._compute_can_approve()
        for holiday in self:
            if holiday.multi_level_validation:
                holiday.can_approve = holiday.state == 'confirm' and self.env.uid in holiday.user_ids.ids

    @api.depends_context('uid')
    @api.depends('state', 'employee_id', 'department_id', 'multi_level_validation', 'user_ids')
    def _compute_can_validate(self):
        """Compute whether the current user can directly validate multi-level leave."""
        super()._compute_can_validate()
        for holiday in self:
            if holiday.multi_level_validation:
                holiday.can_validate = False

    @api.depends_context('uid')
    @api.depends('state', 'employee_id', 'department_id', 'multi_level_validation', 'validation_status_ids.user_id')
    def _compute_can_refuse(self):
        """Compute whether the current user can refuse the multi-level leave request."""
        super()._compute_can_refuse()
        for holiday in self:
            if holiday.multi_level_validation:
                is_validator = self.env.uid in holiday.validation_status_ids.user_id.ids
                is_hr_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
                holiday.can_refuse = holiday.state in ('confirm', 'validate1', 'validate') and (is_validator or is_hr_manager)

    def action_approve(self, check_state=True):
        """Override action_approve to support multi level approval"""
        if self.env.context.get('leave_multi_create'):
            # When creating a leave with multi-level approval, do not auto-approve; stay in confirm state
            multi_leaves = self.filtered('multi_level_validation')
            if multi_leaves:
                standard_leaves = self - multi_leaves
                if standard_leaves:
                    return super(HrLeave, standard_leaves).action_approve(check_state=check_state)
                return True

        multi_leaves = self.filtered('multi_level_validation')
        standard_leaves = self - multi_leaves
        res = True
        if standard_leaves:
            res = super(HrLeave, standard_leaves).action_approve(check_state=check_state)
        if multi_leaves:
            for holiday in multi_leaves:
                if holiday.state != 'confirm':
                    raise UserError(_(
                        'Leave request must be confirmed ("To Approve") in order to approve it.'))
                if self.env.uid not in holiday.user_ids.ids:
                    raise UserError(_('You are not authorized to approve this leave request.'))
                # Mark current user as approved
                for val in holiday.validation_status_ids:
                    if val.user_id.id == self.env.uid:
                        val.validation_status = True
                # If all validators have approved
                if all(val.validation_status for val in holiday.validation_status_ids):
                    current_employee = self.env.user.employee_id
                    if holiday.validation_type == 'both':
                        holiday.sudo().write({
                            'state': 'validate1',
                            'first_approver_id': current_employee.id,
                        })
                    else:
                        holiday.sudo()._action_validate(check_state=False)
                    if not holiday.env.context.get('leave_fast_create'):
                        holiday.activity_update()
        return res

    def action_refuse(self):
        """Override to refuse the leave request if current user is validator or HR manager"""
        multi_leaves = self.filtered('multi_level_validation')
        standard_leaves = self - multi_leaves
        res = True
        if standard_leaves:
            res = super(HrLeave, standard_leaves).action_refuse()
        if multi_leaves:
            for holiday in multi_leaves:
                is_validator = self.env.uid in holiday.validation_status_ids.user_id.ids
                is_hr_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
                if not (is_validator or is_hr_manager):
                    raise UserError(_('You are not authorized to refuse this leave request.'))
                for val in holiday.validation_status_ids:
                    if val.user_id.id == self.env.uid:
                        val.validation_status = False
            res = super(HrLeave, multi_leaves.sudo()).action_refuse()
        return res

    def action_draft(self):
        """Reset all validation statuses when leave request is reset to draft"""
        res = super().action_draft()
        for holiday in self:
            holiday.validation_status_ids.write({'validation_status': False})
        return res

    def action_back_to_approval(self):
        """Reset all validation statuses when leave request moved back to approval"""
        multi_leaves = self.filtered('multi_level_validation')
        if multi_leaves:
            multi_leaves._move_validate_leave_to_confirm()
            multi_leaves.validation_status_ids.write({'validation_status': False})
        non_multi = self - multi_leaves
        if non_multi:
            super(HrLeave, non_multi).action_back_to_approval()
        return True

    def _check_approval_update(self, state, raise_if_not_possible=True):
        """Allow multi-level validators to update leave state during approval/refusal"""
        multi_leaves = self.filtered('multi_level_validation')
        for holiday in multi_leaves:
            if self.env.uid in holiday.validation_status_ids.user_id.ids:
                continue
            super(HrLeave, holiday)._check_approval_update(state, raise_if_not_possible=raise_if_not_possible)
        non_multi = self - multi_leaves
        if non_multi:
            return super(HrLeave, non_multi)._check_approval_update(state, raise_if_not_possible=raise_if_not_possible)
        return True

    def _get_approval_requests(self):
        """Action for Approvals menu item to show approval requests assigned to current user"""
        return {
            'name': _('Approval Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'list,form',
            'domain': [
                ('state', '=', 'confirm'),
                ('validation_status_ids.user_id', '=', self.env.uid),
                ('validation_status_ids.validation_status', '=', False),
            ],
            'target': 'current',
            'context': {'create': False},
        }
