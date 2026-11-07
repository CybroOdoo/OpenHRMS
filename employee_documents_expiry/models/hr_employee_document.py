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
from datetime import timedelta
from markupsafe import escape
from odoo import api, fields, models


class HrEmployeeDocument(models.Model):
    """Create a new module for retrieving document files, allowing users
     to input details about the documents."""
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'

    name = fields.Char(string='Document Number', required=True, copy=False,
                       help="Enter Document Number")
    document_id = fields.Many2one('employee.checklist',
                                  required=True,
                                  help="Choose Employee Checklist for"
                                       " Employee Document")
    description = fields.Text(copy=False,
                              help="Description for Employee Document")
    expiry_date = fields.Date(copy=False,
                              help="Choose Expiry Date for Employee Document")
    employee_id = fields.Many2one('hr.employee', copy=False,
                                  help="Choose Employee for Employee Document")
    company_id = fields.Many2one('res.company',
                                 related='employee_id.company_id',
                                 store=True, index=True,
                                 help="Company of the employee")
    doc_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_employee_document_ir_attachment_rel',
        'document_id', 'attachment_id',
        string="Attachment",
        help="You can attach the copy of your document here.",
        copy=False,
    )
    issue_date = fields.Date(default=fields.Date.context_today, copy=False,
                             help="Choose Issue Date for Employee Document")

    def mail_reminder(self):
        """Function for scheduling emails to send reminders
        about document expiry dates."""
        today = fields.Date.today()
        expiring_docs = self.search([
            ('expiry_date', '>=', today),
            ('expiry_date', '<=', today + timedelta(days=7)),
            ('employee_id.work_email', '!=', False),
        ])
        mail_values_list = []
        for doc in expiring_docs:
            employee_name = escape(
                doc.employee_id.name or self.env._("Employee")
            )
            doc_name = escape(doc.name or "")
            mail_content = self.env._(
                "Hello %(employee)s,<br>Your document %(doc_name)s "
                "is going to expire on %(expiry_date)s. Please renew it "
                "before the expiry date.",
                employee=employee_name,
                doc_name=doc_name,
                expiry_date=doc.expiry_date,
            )
            subject = self.env._(
                "Document %(name)s Expiring on %(date)s",
                name=doc.name,
                date=doc.expiry_date,
            )
            mail_values_list.append({
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': doc.employee_id.work_email,
            })
        if mail_values_list:
            self.env['mail.mail'].sudo().create(mail_values_list)

    @api.onchange('expiry_date')
    def _onchange_expiry_date(self):
        """Function to obtain a validation error for expired documents."""
        if self.expiry_date and self.expiry_date < fields.Date.today():
            return {
                'warning': {
                    'title': self.env._('Document Expired'),
                    'message': self.env._("Your document has already expired.")
                }
            }
        return False
