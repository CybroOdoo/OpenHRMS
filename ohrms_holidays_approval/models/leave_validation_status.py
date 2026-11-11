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


class LeaveValidationStatus(models.Model):
    """Model for leave validators and their status for each leave request"""
    _name = 'leave.validation.status'
    _description = 'Leave Validation Status'

    leave_id = fields.Many2one('hr.leave', string='Leave',
                               ondelete='cascade',
                               help='Leave record')
    user_id = fields.Many2one('res.users',
                              string='Leave Validators',
                              help="Indicates the validators of leave",
                              domain="[('share','=',False)]")
    validation_status = fields.Boolean(string='Approve Status', readonly=True,
                                       help="Status of leave approval")
    leave_comments = fields.Text(string='Comments',
                                 help="Comments regarding the request")

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Prevent Changing leave validators on existing records from leave request form"""
        if self._origin.id:
            raise UserError(_(
                "Changing leave validators is not permitted. You can only change "
                "it from Leave Types Configuration"))
