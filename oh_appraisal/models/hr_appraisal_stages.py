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
from odoo import fields, models


class HrAppraisalStages(models.Model):
    """Create the model Appraisal Stages to show the stages of the appraisal"""
    _name = 'hr.appraisal.stages'
    _description = 'Appraisal Stages'

    name = fields.Char(string="Name", help="Name of the appraisal stage")
    sequence = fields.Integer(string="Sequence",
                              help="Sequence of the appraisal stage to be "
                                   "shown")
    fold = fields.Boolean(string='Folded in Appraisal Pipeline',
                          help='This stage is folded in the kanban view when '
                               'there are no records in that stage to display.')
