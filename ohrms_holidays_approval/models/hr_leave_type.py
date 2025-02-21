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
from odoo import api, fields, models


class HrLeaveType(models.Model):
    """ Extend model to add multilevel approval"""
    _inherit = 'hr.leave.type'

    multi_level_validation = fields.Boolean(
        string='Multiple Level Approval',
        help="If checked then multi-level approval is necessary",
        compute='_compute_multi_level_validation')
    leave_validation_type = fields.Selection(
        selection_add=[('multi', 'Multi Level Approval')])
    validator_ids = fields.Many2many('hr.holidays.validators',
                                     string='Leave Validators',
                                     help="Indicates the leave validators")

    @api.depends('leave_validation_type')
    def _compute_multi_level_validation(self):
        """Method for validating the value of multi_level_validation"""
        for rec in self:
            rec.multi_level_validation = True if (
                    rec.leave_validation_type == 'multi') else False
