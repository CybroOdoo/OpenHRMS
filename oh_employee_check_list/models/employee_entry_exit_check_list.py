# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Nilmar Shereef (<https://www.cybrosys.com>)
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
###################################################################################
from odoo import models, fields, api


class EmployeeEntryDocuments(models.Model):
    _name = 'employee.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Documents"

    @api.multi
    def name_get(self):
        result = []
        for each in self:
            if each.document_type == 'entry':
                name = each.name + '_en'
            elif each.document_type == 'exit':
                name = each.name + '_ex'
            elif each.document_type == 'other':
                name = each.name + '_ot'
            result.append((each.id, name))
        return result

    name = fields.Char(string='Name', copy=False, required=1)
    document_type = fields.Selection([('entry', 'Entry Process'),
                                      ('exit', 'Exit Process'),
                                      ('other', 'Other')], string='Checklist Type', help='Type of Checklist', readonly=1, required=1)


class HrEmployeeDocumentInherit(models.Model):
    _inherit = 'hr.employee.document'

    document_name = fields.Many2one('employee.checklist', string='Document', help='Type of Document', required=True)

