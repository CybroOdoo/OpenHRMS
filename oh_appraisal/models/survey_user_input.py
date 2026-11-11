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
from odoo import api, fields, models


class SurveyUserInput(models.Model):
    """Inherits the model survey.user_input to extend the model and make
    changes in the functionality."""
    _inherit = 'survey.user_input'

    appraisal_id = fields.Many2one('hr.appraisal', string="Appraisal id",
                                   help="Appraisal ID of the user input for "
                                        "the survey")

    @api.model_create_multi
    def create(self, vals_list):
        """inherits the create method of the model survey.user_input"""
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model') == 'hr.appraisal':
            for vals in vals_list:
                vals.setdefault('appraisal_id', ctx.get('active_id'))
        return super().create(vals_list)
