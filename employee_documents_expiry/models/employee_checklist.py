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
from odoo import api, fields, models


class EmployeeChecklist(models.Model):
    """Create an 'employee_checklist' model to incorporate
    details about document types"""
    _name = 'employee.checklist'
    _inherit = 'mail.thread'
    _description = "Employee Checklist"

    name = fields.Char(string='Document Name', copy=False, required=True,
                       help="Enter Document Name")
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')],
                                     string='Checklist Type', required=True,
                                     help="Select checklist type for document")

    @api.depends('document_type', 'name')
    def _compute_display_name(self):
        """Compute the display name based on document type."""
        suffix_map = {
            'entry': 'en',
            'exit': 'ex',
            'other': 'ot',
        }
        for rec in self:
            suffix = suffix_map.get(rec.document_type)
            if suffix and rec.name:
                rec.display_name = f"{rec.name} - {suffix}"
            else:
                rec.display_name = rec.name
