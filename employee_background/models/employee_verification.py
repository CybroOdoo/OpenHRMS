# -*- coding: utf-8 -*-
#############################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
###############################################################################
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EmployeeVerification(models.Model):
    """Creates the model Employee Verification"""
    _name = 'employee.verification'
    _description = "Employee Verification"

    name = fields.Char(string='ID', readonly=True, copy=False,
                       help="Verification Id")
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True,
                                  help='You can choose the employee for '
                                       'background verification')
    address_id = fields.Many2one(related='employee_id.address_id',
                                 string='Address', readonly=False,
                                 help="Address of the employee")
    assigned_id = fields.Many2one('res.users', string='Assigned By',
                                  readonly=1,
                                  default=lambda self: self.env.uid,
                                  help="Assigned Login User")
    agency_id = fields.Many2one('res.partner', string='Agency',
                                domain=[('verification_agent', '=', True)],
                                help='You can choose a Verification Agent')
    resume_ids = fields.Many2many('ir.attachment',
                                  string="Resume of Applicant",
                                  help='You can attach the copy of your '
                                       'document',
                                  copy=False)
    description_by_agency = fields.Char(string='Description', readonly=True,
                                        help="Description by agency")
    assigned_date = fields.Date(string="Assigned Date", readonly=True,
                                default=date.today(),
                                help="Record Assigned Date")
    expected_date = fields.Date(state='Expected Date',
                                help='Expected date of completion of '
                                     'background verification')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assign', 'Assigned'),
        ('submit', 'Verification Completed'),
    ], string='Status', default='draft')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 help="Company of the current record")
    agency_attachment_ids = fields.Many2many('ir.attachment',
                                             'agency_attachments_rel',
                                             'verification', 'attachment',
                                             string="Agency Attachment",
                                             help='Attachment from the agency',
                                             copy=False, readonly=True)

    def action_assign_statusbar(self):
        """Method action_assign_statusbar will assign the verification
        of the contact to an agency and mail to agency"""
        if self.agency_id:
            if self.address_id or self.resume_ids:
                self.state = 'assign'
                template = self.env.ref(
                    'employee_background.assign_agency_email_template')
                self.env['mail.template'].browse(template.id).send_mail(
                    self.id,
                    force_send=True)
            else:
                raise UserError(
                    _("There should be at least address or resume"
                      " of the employee."))
        else:
            raise UserError(
                _("Agency is not assigned. Please select one of the Agency."))

    @api.model
    def create(self, vals):
        """Supering the create method of the model Employee Verification and
        also adding verification_id into the vals for creating the record."""
        seq = self.env['ir.sequence'].next_by_code(
            'employee.verification') or '/'
        vals['name'] = seq
        return super(EmployeeVerification, self).create(vals)

    def unlink(self):
        """Supering the unlink method of the model Employee Verification to
        raise an error when unlinking the record in model which is not in draft
        state"""
        for record in self:
            if record.state not in 'draft':
                raise UserError(
                    _('You cannot delete the verification created.'))
            super(EmployeeVerification, record).unlink()
