# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from datetime import date, datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrCustody(models.Model):
    """
        Hr custody contract creation model.
    """
    _name = 'hr.custody'
    _description = 'Hr Custody Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    is_read_only = fields.Boolean(string="Check Field")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """ Use this function to check weather
        the user has the permission
        to change the employee"""
        res_user = self.env['res.users'].browse(self._uid)
        if res_user.has_group('hr.group_hr_user'):
            self.is_read_only = True
        else:
            self.is_read_only = False

    def mail_reminder(self):
        """ Use this function to product return reminder mail"""
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([('state', '=', 'approved')])
        for i in match:
            if i.return_date:
                exp_date = fields.Date.from_string(i.return_date)
                if exp_date <= date_now:
                    base_url = self.env['ir.config_parameter'].get_param(
                        'web.base.url')
                    url = base_url + _(
                        '/web#id=%s&view_type=form&model=hr.custody&menu_id=') % i.id
                    mail_content = _(
                        'Hi %s,<br>As per the %s you took %s on %s for the reason of %s. S0 here we '
                        'remind you that you have to return that on or before %s. Otherwise, you can '
                        'renew the reference number(%s) by extending the return date through following '
                        'link.<br> <div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                        'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                        'border-color:#875A7B;text-decoration: none; display: inline-block; '
                        'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                        'cursor: pointer; white-space: nowrap; background-image: none; '
                        'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                        'Renew %s</a></div>') % \
                                   (i.employee_id.name, i.name,
                                    i.custody_property_id.name,
                                    i.date_request, i.purpose,
                                    date_now, i.name, url, i.name)
                    main_content = {
                        'subject': _('REMINDER On %s') % i.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee_id.work_email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                    if i.employee_id.user_id:
                        mail_id.mail_message_id.write({
                            'partner_ids': [
                                (4, i.employee_id.user_id.partner_id.id)]})

    @api.model_create_multi
    def create(self, vals):
        """Create a new record for the HrCustody model.
            This method is responsible for creating a new
            record for the HrCustody model with the provided values.
            It automatically generates a unique name for
            the record using the 'ir.sequence'
            and assigns it to the 'name' field."""
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('hr.custody')
        return super(HrCustody, self).create(vals)

    def sent(self):
        """Move the current record to the 'to_approve' state."""
        self.state = 'to_approve'

    def send_mail(self):
        """Send email notification using a predefined template."""
        template = self.env.ref(
            'hr_custody.custody_email_notification_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.is_mail_send = True

    def set_to_draft(self):
        """Set the current record to the 'draft' state."""
        self.state = 'draft'

    def renew_approve(self):
        """The function Used to renew and approve
        the current custody record."""
        for custody in self.env['hr.custody']. \
                search([('custody_property_id', '=',
                         self.custody_property_id.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.return_date = self.renew_date
        self.renew_date = ''
        self.state = 'approved'

    def renew_refuse(self):
        """the function used to refuse
        the renewal of the current custody record"""
        for custody in self.env['hr.custody']. \
                search([('custody_property_id', '=',
                         self.custody_property_id.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.renew_date = ''
        self.state = 'approved'

    def approve(self):
        """The function used to approve
        the current custody record."""
        for custody in self.env['hr.custody'].search(
                [('custody_property_id', '=', self.custody_property_id.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.state = 'approved'

    def set_to_return(self):
        """The function used to set the current
        custody record to the 'returned' state"""
        self.state = 'returned'
        self.return_date = date.today()

    @api.constrains('return_date')
    def validate_return_date(self):
        """The function validate the return
        date to ensure it is after the request date"""
        if self.return_date < self.date_request:
            raise ValidationError(_('Please Give Valid Return Date'))

    name = fields.Char(string='Code', copy=False,
                       help='A unique code assigned to this record.')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 hhelp='The company associated'
                                       ' with this record. ',
                                 default=lambda self: self.env.user.company_id)
    rejected_reason = fields.Text(string='Rejected Reason', copy=False,
                                  readonly=1, help="Reason for the rejection")
    renew_rejected_reason = fields.Text(string='Renew Rejected Reason',
                                        copy=False, readonly=1,
                                        help="Renew rejected reason")
    date_request = fields.Date(string='Requested Date', required=True,
                               track_visibility='always',
                               help='The date when the request was made',
                               default=datetime.now().strftime('%Y-%m-%d'))
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True,
                                  help='The employee associated with '
                                       'this record.',
                                  default=lambda
                                      self: self.env.user.employee_id.id, )
    purpose = fields.Char(string='Reason', track_visibility='always',
                          required=True,
                          help='The reason or purpose of the custody')
    custody_property_id = fields.Many2one('custody.property',
                                          string='Property', required=True,
                                          help='The property associated '
                                               'with this custody record'
                                          )
    return_date = fields.Date(string='Return Date', required=True,
                              track_visibility='always',
                              help='The date when the custody '
                                   'is expected to be returned. ')
    renew_date = fields.Date(string='Renewal Return Date',
                             track_visibility='always',
                             help="Return date for the renewal", readonly=True,
                             copy=False)
    notes = fields.Html(string='Notes', help='Note for Custody')
    is_renew_return_date = fields.Boolean(default=False, copy=False,
                                          help='Rejected Renew Date')
    is_renew_reject = fields.Boolean(default=False, copy=False,
                                     help='Indicates whether '
                                          'the renewal is rejected or not.')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'Waiting For Approval'),
         ('approved', 'Approved'),
         ('returned', 'Returned'), ('rejected', 'Refused')], string='Status',
        default='draft',
        track_visibility='always', help='Custody states visible in statusbar')
    is_mail_send = fields.Boolean(string="Mail Send",
                                  help='Indicates whether an email has '
                                       'been sent or not.')
