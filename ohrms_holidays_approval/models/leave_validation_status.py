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


class LeaveValidationStatus(models.Model):
    """ Model for leave validators and their status for each leave request """
    _name = 'leave.validation.status'
    _description = 'Leave Validation Status'

    leave_id = fields.Many2one('hr.leave', string='Leave',
                               help='Leave record')
    user_id = fields.Many2one('res.users',
                              string='Leave Validators',
                              help="Indicates the validators of leave",
                              domain="[('share','=',False)]")
    validation_status = fields.Boolean(string='Approve Status', readonly=True,
                                       track_visibility='always',
                                       help="Status of leave approval")
    leave_comments = fields.Text(string='Comments',
                                 help="Comments regarding the request")

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """ Prevent Changing leave validators from leave request form"""
        raise UserError(_(
            "Changing leave validators is not permitted. You can only change "
            "it from Leave Types Configuration"))
