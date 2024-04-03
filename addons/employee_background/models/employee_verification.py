# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
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
###################################################################################
import base64
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests


class EmployeeVerification(models.Model):
    _name = 'employee.verification'
    _rec_name = 'verification_id'

    verification_id = fields.Char('ID', readonly=True, copy=False, help="Verification Id")
    employee = fields.Many2one('hr.employee', string='Employee', required=True,
                               help='You can choose the employee for background verification')
    address = fields.Many2one(related='employee.address_home_id', string='Address', readonly=False)
    assigned_by = fields.Many2one('res.users', string='Assigned By', readonly=1, default=lambda self: self.env.uid,
                                  help="Assigned Login User")
    agency = fields.Many2one('res.partner', string='Agency', domain=[('verification_agent', '=', True)],
                             help='You can choose a Verification Agent')
    resume_uploaded = fields.Many2many('ir.attachment', string="Resume of Applicant",
                                       help='You can attach the copy of your document', copy=False)
    description_by_agency = fields.Char(string='Description', readonly=True, help="Description")
    agency_attachment_id = fields.Many2one('ir.attachment', string='Attachment', help='Attachment from Agency')
    field_check = fields.Boolean(string='Check', invisible=True)
    assigned_date = fields.Date(string="Assigned Date", readonly=True, default=date.today(),
                                help="Record Assigned Date")
    expected_date = fields.Date(state='Expected Date', help='Expected date of completion of background verification')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assigned'),
        ('submit', 'Verification Completed'),
    ], string='Status', default='draft')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company'].browse(1))

    def download_attachment(self):
        if self.agency_attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/image?model=ir.attachment&field=datas&id=%s&filename=%s' % (
                    self.agency_attachment_id.id, self.agency_attachment_id.name),
            }
        else:
            raise UserError(_("No attachments available."))

    def assign_statusbar(self):
        if self.agency:
            if self.address or self.resume_uploaded:
                self.state = 'assign'
                template = self.env.ref('employee_background.assign_agency_email_template')
                print("5555",template)
                self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
            else:
                raise UserError(_("There should be at least address or resume of the employee."))
        else:
            raise UserError(_("Agency is not assigned. Please select one of the Agency."))

    # sequence generation for employee verification
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('res.users') or '/'
        vals['verification_id'] = seq
        return super(EmployeeVerification, self).create(vals)

    def unlink(self):
        if self.state not in 'draft':
            raise UserError(_('You cannot delete the verification created.'))
        super(EmployeeVerification, self).unlink()
