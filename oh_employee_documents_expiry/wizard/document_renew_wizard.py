# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, Command
from odoo.exceptions import UserError
from markupsafe import Markup

class DocumentRenewWizard(models.TransientModel):
    """Wizard to handle the manual renewal process of an employee document. 
    This transient model collects the new issue date, expiry date, attachments, 
    and renewal reason before updating the original document and archiving the old data."""
    
    _name = 'document.renew.wizard'
    _description = 'Renew Employee Document'

    issue_date = fields.Date(string='New Issue Date', required=True, default=fields.Date.context_today)
    expiry_date = fields.Date(string='New Expiry Date', required=True)
    doc_attachment_ids = fields.Many2many('ir.attachment', string="New Attachments", required=True)
    renewal_reason = fields.Text(string='Renewal Reason', required=True)

    def action_confirm_renew(self):
        """Update the original document with new dates and attachments, 
        archive the previous state into the document history, and set the state to active.
        """
        self.ensure_one()
        if self.expiry_date <= fields.Date.context_today(self):
            raise UserError("New expiry date must be strictly in the future.")
        if self.issue_date and self.expiry_date <= self.issue_date:
            raise UserError("New expiry date must be after the issue date.")
            
        document_id = self.env.context.get('active_id')
        if document_id:
            document = self.env['hr.employee.document'].browse(document_id)
            
            # Archive to history
            self.env['hr.employee.document.history'].create({
                'document_id': document.id,
                'issue_date': document.issue_date,
                'expiry_date': document.expiry_date,
                'attachment_ids': [Command.set(document.doc_attachment_ids.ids)],
                'renewal_reason': self.renewal_reason,
            })
            
            old_expiry = document.expiry_date
            
            # Replace attachments and update dates
            document.write({
                'issue_date': self.issue_date,
                'expiry_date': self.expiry_date,
                'doc_attachment_ids': [Command.set(self.doc_attachment_ids.ids)],
                'state': 'active'
            })
            
            # Log chatter message
            msg = Markup("""
                <b>Document renewed</b><br/>
                <b>Previous Expiry:</b> %s<br/>
                <b>New Expiry:</b> %s<br/>
                <b>Reason:</b> %s
            """) % (old_expiry or 'None', self.expiry_date, self.renewal_reason)
            document.message_post(body=msg)
