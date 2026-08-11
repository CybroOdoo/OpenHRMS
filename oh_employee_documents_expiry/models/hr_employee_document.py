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
from datetime import date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployeeDocument(models.Model):
    """This class represents HR employee documents and provides methods
    for managing document expiry notifications."""
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired')
    ], string='Status', default='draft', tracking=True)

    name = fields.Char(string='Document Number', copy=False, readonly=True,
                       help='Auto-generated document reference number.')
    description = fields.Text(string='Description', copy=False,
                              help="Description of the documents.")
    expiry_date = fields.Date(string='Expiry Date', copy=False,
                              help="Expiry date of the documents.")
    employee_ref_id = fields.Many2one('hr.employee', invisible=1,
                                      copy=False,
                                      help='Specify the employee name.')
    doc_attachment_ids = fields.Many2many('ir.attachment',
                                          'doc_attach_rel',
                                          'doc_id', 'attach_id3',
                                          string="Current Attachment(s)",
                                          help='You can attach the copy of your'
                                               ' document', copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today,
                             help="Date of issued", copy=False)
    document_type_id = fields.Many2one('document.type',
                                       string="Document Type",
                                       help="Type of the document.")
    before_days = fields.Integer(related='document_type_id.before_days', string="Days", store=True, readonly=True)
    notification_type = fields.Selection(related='document_type_id.notification_type', string='Notification Type', store=True, readonly=True)
    
    remaining_days = fields.Integer(string="Remaining Days", compute='_compute_remaining_days', search='_search_remaining_days')
    expiry_status = fields.Char(compute='_compute_expiry_status', string='Status Text')
    history_ids = fields.One2many('hr.employee.document.history', 'document_id', string='Renewal History', readonly=True)
    history_count = fields.Integer(compute='_compute_history_count', string='History Count')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to assign an auto-generated sequence number on save."""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.document') or '/'
        return super().create(vals_list)

    def _search_remaining_days(self, operator, value):
        """Custom search method for filtering documents based on remaining days."""
        target_date = fields.Date.context_today(self) + timedelta(days=value)
        return [('expiry_date', operator, target_date)]

    @api.depends('expiry_date')
    def _compute_remaining_days(self):
        """Compute the number of days remaining until the document expiry date."""
        for rec in self:
            if rec.expiry_date:
                delta = rec.expiry_date - fields.Date.context_today(rec)
                rec.remaining_days = delta.days
            else:
                rec.remaining_days = 0

    @api.depends('expiry_date', 'state')
    def _compute_expiry_status(self):
        """Compute a human-readable text representation of the expiry status."""
        for rec in self:
            if not rec.expiry_date:
                rec.expiry_status = ''
            else:
                delta = rec.expiry_date - fields.Date.context_today(rec)
                if delta.days < 0:
                    rec.expiry_status = _('Expired %s Days') % abs(delta.days)
                elif delta.days == 0:
                    rec.expiry_status = _('Today')
                elif delta.days == 1:
                    rec.expiry_status = _('Tomorrow')
                else:
                    rec.expiry_status = str(delta.days)

    @api.depends('history_ids')
    def _compute_history_count(self):
        """Compute the total number of renewal history records for the document."""
        for rec in self:
            rec.history_count = len(rec.history_ids)

    def action_view_history(self):
        """Open a view showing the renewal history records for this document."""
        self.ensure_one()
        return {
            'name': _('Renewal History'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee.document.history',
            'view_mode': 'list,form',
            'domain': [('document_id', '=', self.id)],
            'context': {'default_document_id': self.id},
        }

    @api.constrains('document_type_id', 'employee_ref_id', 'state')
    def _check_duplicate_active_documents(self):
        """Ensure that an employee can only have one active document of a specific type."""
        for rec in self:
            if rec.state == 'active' and rec.document_type_id and rec.employee_ref_id:
                domain = [
                    ('employee_ref_id', '=', rec.employee_ref_id.id),
                    ('document_type_id', '=', rec.document_type_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', rec.id)
                ]
                if self.search_count(domain) > 0:
                    raise UserError(_("Employee already has an active document of this type. Renew the existing one instead."))

    def action_active(self):
        """Set document to active state."""
        for rec in self:
            if rec.expiry_date and rec.expiry_date < fields.Date.context_today(rec):
                raise UserError(_('You cannot validate a document that is already expired.'))
        self.write({'state': 'active'})

    def action_expired(self):
        """Set document to expired state."""
        self.write({'state': 'expired'})

    def action_draft(self):
        """Set document to draft state."""
        self.write({'state': 'draft'})



    def mail_reminder(self):
        """Sending document expiry notification to employees."""
        # Automatically expire documents whose expiry date has passed
        expired_documents = self.search([
            ('expiry_date', '<', fields.Date.today()),
            ('state', 'in', ['draft', 'active'])
        ])
        if expired_documents:
            expired_documents.action_expired()

        for record in self.search([('expiry_date', '!=', False), ('state', 'in', ['draft', 'active', 'expired'])]):
            exp_date = fields.Date.from_string(record.expiry_date)
            days_before = timedelta(days=record.before_days or 0)
            is_expiry_today = fields.Date.today() == exp_date
            is_notification_day = any([
                record.notification_type == 'single' and is_expiry_today,
                record.notification_type == 'multi' and (fields.Date.today() == exp_date - days_before or is_expiry_today),
                record.notification_type == 'everyday' and fields.Date.today() >= exp_date - days_before and fields.Date.today() <= exp_date,
                record.notification_type == 'everyday_after' and fields.Date.today() >= exp_date and fields.Date.today() <= exp_date + days_before,
                not record.notification_type and fields.Date.today() == exp_date - timedelta(days=7),
            ])
            if is_notification_day:
                employee_name = record.employee_ref_id.name
                document_name = record.name
                expiry_date_str = str(record.expiry_date)
                mail_content = (
                    f"Hello {employee_name},<br>Your Document {document_name} "
                    f"is going to expire on {expiry_date_str}. "
                    "Please renew it before the expiry date."
                )
                subject = _('Document-%s Expired On %s') % (
                    document_name, expiry_date_str)
                main_content = {
                    'subject': subject,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': record.employee_ref_id.work_email,
                }
                self.env['mail.mail'].create(main_content).send()
                
                manager_id = record.employee_ref_id.parent_id.user_id.id or record.employee_ref_id.user_id.id or 2
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Document Expiry: %s - %s') % (record.employee_ref_id.name, record.document_type_id.name),
                    note=_('Please review the expiring document (%s).') % record.name,
                    user_id=manager_id,
                    date_deadline=record.expiry_date
                )

    def action_send_manual_reminder(self):
        """Manually send document expiry notification to the employee."""
        for record in self:
            if not record.expiry_date:
                continue
            employee_name = record.employee_ref_id.name
            document_name = record.name
            expiry_date_str = str(record.expiry_date)
            mail_content = (
                f"Hello {employee_name},<br>This is a reminder that your Document {document_name} "
                f"is going to expire on {expiry_date_str}. "
                "Please renew it before the expiry date."
            )
            subject = _('Reminder: Document-%s Expiring On %s') % (
                document_name, expiry_date_str)
            main_content = {
                'subject': subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': record.employee_ref_id.work_email,
            }
            self.env['mail.mail'].create(main_content).send()
        return True

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        """This method is called as a constraint whenever the 'expiry_date'
         field of an 'hr.employee.document' record is modified."""
        for rec in self:
            if rec.expiry_date:
                exp_date = fields.Date.from_string(rec.expiry_date)
                if exp_date < date.today():
                    raise UserError(_('Your Document Is Expired.'))

    def action_open_employee(self):
        """ Opens the linked employee's profile. """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'res_id': self.employee_ref_id.id,
            'target': 'current',
        }

    def action_renew(self):
        """ Open wizard to renew document. """
        self.ensure_one()
        return {
            'name': _('Renew Document'),
            'type': 'ir.actions.act_window',
            'res_model': 'document.renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }
