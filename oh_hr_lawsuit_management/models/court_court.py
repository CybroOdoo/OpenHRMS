# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CourtCourt(models.Model):
    """Class holding court details."""
    _name = 'court.court'
    _description = 'Court'

    name = fields.Char(string='Court', help='Name of Court')
    judge_id = fields.Many2one('res.partner', string='Judge',
                               domain="[('is_judge', '=', True)]",
                               help='Name of the Judge')

    @api.constrains('judge_id')
    def _check_judge_id(self):
        """Ensure the selected Judge is flagged as a judge on their
        contact, since the view domain alone does not stop this being
        bypassed via write/import/API calls."""
        for court in self:
            if court.judge_id and not court.judge_id.is_judge:
                raise ValidationError(
                    "The selected Judge must have the 'Judge' checkbox "
                    "enabled on their contact.")
