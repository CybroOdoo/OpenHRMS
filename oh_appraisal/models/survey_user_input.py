# -*- coding: utf-8 -*-
###############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models


class SurveyUserInput(models.Model):
    """Inherits the model survey.user_input to extend the model and make
    changes in the functionality."""
    _inherit = 'survey.user_input'

    appraisal_id = fields.Many2one('hr.appraisal', string="Appraisal id",
                                   help="Appraisal ID of the user input for "
                                        "the survey")

    @api.model
    def create(self, vals):
        """inherits the create method of the model survey.user_input"""
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model') == 'hr.appraisal':
            vals['appraisal_id'] = ctx.get('active_id')
        return super(SurveyUserInput, self).create(vals)
