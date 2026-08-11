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
from odoo import fields, models

class HrEmployeeDocumentHistory(models.Model):
    """Model to store the historical states and attachments of employee documents
    prior to their manual renewal. Serves as a read-only audit trail."""
    
    _name = 'hr.employee.document.history'
    _description = 'Employee Document Renewal History'
    _order = 'renewed_on desc'

    document_id = fields.Many2one('hr.employee.document', string='Document', required=True, ondelete='cascade')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment(s)')
    renewed_by = fields.Many2one('res.users', string='Renewed By', default=lambda self: self.env.user)
    renewed_on = fields.Datetime(string='Renewal Date', default=fields.Datetime.now)
    renewal_reason = fields.Text(string='Renewal Reason')
