# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Unnimaya C O (odoo@cybrosys.com)
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
###############################################################################
from odoo import fields, models, _


class HrEmployee(models.Model):
    """Inherited to add more fields and functions"""
    _inherit = 'hr.employee'

    legal_count = fields.Integer(compute='_compute_legal_count',
                                 string='Legal Actions', help='Number of legal'
                                                              'actions')

    def _compute_legal_count(self):
        """Method for computing legal count"""
        for each in self:
            each.legal_count = self.env['hr.lawsuit'].search_count(
                [('employee_id', '=', each.id)])

    def action_view_legal(self):
        """Method for retrieving all legal actions of an employee"""
        for employee in self:
            return {
                'domain': str(
                    [('id', 'in', self.env['hr.lawsuit'].sudo().search(
                        [('employee_id', '=', employee.id)]).ids)]),
                'view_mode': 'tree,form',
                'res_model': 'hr.lawsuit',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'name': _('Legal Actions')
            }
