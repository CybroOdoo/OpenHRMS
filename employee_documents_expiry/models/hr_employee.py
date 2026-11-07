# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
###############################################################################
from odoo import fields, models


class HrEmployee(models.Model):
    """Inherit 'hr.employee' to add 'Checklist Documents' smart button."""
    _inherit = 'hr.employee'

    document_expiry_count = fields.Integer(
        compute='_compute_document_expiry_count',
        string='# Checklist Documents',
        help="Get total count of Checklist Documents for an Employee")

    def _compute_document_expiry_count(self):
        """Function to obtain the total count of documents."""
        document_data = self.env['hr.employee.document']._read_group(
            [('employee_id', 'in', self.ids)],
            ['employee_id'],
            ['__count'],
        )
        data_mapped = {
            employee.id: count for employee, count in document_data
            if employee
        }
        for rec in self:
            rec.document_expiry_count = data_mapped.get(rec.id, 0)

    def action_document_view(self):
        """Function to open the 'hr_employee_document' model."""
        self.ensure_one()
        return {
            'name': self.env._('Checklist Documents'),
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'help': self.env._(
                '<p class="o_view_nocontent_smiling_face">'
                'Create and track checklist documents for this employee.'
                '</p>'
            ),
            'limit': 80,
            'context': {'default_employee_id': self.id}
        }
