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
from odoo.tools.sql import column_exists, rename_column, table_exists


def migrate(cr, version):
    """Migrate legacy doc_attach_ids table and columns to standard Odoo 19
    hr_employee_document_ir_attachment_rel."""
    if table_exists(cr, 'doc_attach_ids') and not table_exists(
        cr, 'hr_employee_document_ir_attachment_rel'
    ):
        cr.execute(
            "ALTER TABLE doc_attach_ids "
            "RENAME TO hr_employee_document_ir_attachment_rel"
        )
    if column_exists(cr, 'hr_employee_document_ir_attachment_rel', 'doc_id'):
        rename_column(
            cr, 'hr_employee_document_ir_attachment_rel',
            'doc_id', 'document_id'
        )
    if column_exists(
        cr, 'hr_employee_document_ir_attachment_rel', 'attach_id3'
    ):
        rename_column(
            cr, 'hr_employee_document_ir_attachment_rel',
            'attach_id3', 'attachment_id'
        )
