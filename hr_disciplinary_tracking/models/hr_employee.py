# -- coding: utf-8 --
###############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys (<https://www.cybrosys.com>)
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


class HrEmployee(models.Model):
    """Inherit this module to compute the disciplinary action count"""
    _inherit = 'hr.employee'

    discipline_count = fields.Integer(compute="_compute_discipline_count")

    def _compute_discipline_count(self):
        """Compute the employee details based on the discipline count"""
        all_actions = self.env['disciplinary.action'].read_group([
            ('employee_name', 'in', self.ids),
            ('state', '=', 'action'),
        ], fields=['employee_name'], groupby=['employee_name'])
        mapping = dict(
            [(action['employee_name'][0], action['employee_name_count']) for
             action in all_actions])
        for employee in self:
            employee.discipline_count = mapping.get(employee.id, 0)
