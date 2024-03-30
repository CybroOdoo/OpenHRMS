# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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


class HrEmployeeDocument(models.Model):
    """Inherit hr_employee_document for adding entry and exit processes
    in documents"""
    _inherit = 'hr.employee.document'

    document_id = fields.Many2one('employee.checklist',
                                  string='Checklist Document',
                                  help='Choose the document in the checklist'
                                       'here. Automatically the checklist box'
                                       'become true')

    @api.model
    def create(self, vals):
        """Function for create Employee Documents"""
        result = super(HrEmployeeDocument, self).create(vals)
        if result.document_id.document_type == 'entry':
            result.employee_ref.write(
                {'employee_entry_checklist_ids': [(4, result.document_id.id)]})
        if result.document_id.document_type == 'exit':
            result.employee_ref.write(
                {'employee_exit_checklist_ids': [(4, result.document_id.id)]})
        return result

    def unlink(self):
        """Function for delete Employee Documents"""
        for result in self:
            if result.document_id.document_type == 'entry':
                result.employee_ref.write(
                    {'employee_entry_checklist_ids': [
                        (5, result.document_id.id)]})
            if result.document_id.document_type == 'exit':
                result.employee_ref.write(
                    {'employee_exit_checklist_ids': [
                        (5, result.document_id.id)]})
        res = super(HrEmployeeDocument, self).unlink()
        return res
