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
from datetime import date, datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError


class HrCustody(models.Model):
    """
        Hr custody contract creation model.
        """
    _name = 'hr.custody'
    _description = 'Hr Custody Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    read_only = fields.Boolean(string="check field")

    @api.onchange('employee')
    def _compute_read_only(self):
        """ Use this function to check weather the user has the permission to change the employee"""
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('hr.group_hr_user'):
            self.read_only = True
        else:
            self.read_only = False

    def mail_reminder(self):

        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([('state', '=', 'approved')])
        for i in match:
            if i.return_date:
                exp_date = fields.Date.from_string(i.return_date)
                if exp_date <= date_now:
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    url = base_url + _('/web#id=%s&view_type=form&model=hr.custody&menu_id=') % i.id
                    mail_content = _('Hi %s,<br>As per the %s you took %s on %s for the reason of %s. S0 here we '
                                     'remind you that you have to return that on or before %s. Otherwise, you can '
                                     'renew the reference number(%s) by extending the return date through following '
                                     'link.<br> <div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                                     'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                                     'border-color:#875A7B;text-decoration: none; display: inline-block; '
                                     'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                                     'cursor: pointer; white-space: nowrap; background-image: none; '
                                     'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                                     'Renew %s</a></div>') % \
                                   (i.employee.name, i.name, i.custody_name.name, i.date_request, i.purpose,
                                    date_now, i.name, url, i.name)
                    main_content = {
                        'subject': _('REMINDER On %s') % i.name,
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.employee.work_email,
                    }
                    mail_id = self.env['mail.mail'].create(main_content)
                    mail_id.mail_message_id.body = mail_content
                    mail_id.send()
                    if i.employee.user_id:
                        mail_id.mail_message_id.write({'partner_ids': [(4, i.employee.user_id.partner_id.id)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.custody')
        return super(HrCustody, self).create(vals)

    def sent(self):
        self.state = 'to_approve'

    def send_mail(self):
        template = self.env.ref('hr_custody.custody_email_notification_template')
        self.env['mail.template'].browse(template.id).send_mail(self.id)
        self.mail_send = True

    def set_to_draft(self):
        self.state = 'draft'

    def renew_approve(self):
        for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.return_date = self.renew_date
        self.renew_date = ''
        self.state = 'approved'

    def renew_refuse(self):
        for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.renew_date = ''
        self.state = 'approved'

    def approve(self):
        for custody in self.env['hr.custody'].search([('custody_name', '=', self.custody_name.id)]):
            if custody.state == "approved":
                raise UserError(_("Custody is not available now"))
        self.state = 'approved'

    def set_to_return(self):
        self.state = 'returned'
        self.return_date = date.today()

    # return date validation
    @api.constrains('return_date')
    def validate_return_date(self):
        if self.return_date < self.date_request:
            raise ValidationError(_('Please Give Valid Return Date'))

    name = fields.Char(string='Code', copy=False, help="Code")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id)
    rejected_reason = fields.Text(string='Rejected Reason', copy=False, readonly=1, help="Reason for the rejection")
    renew_rejected_reason = fields.Text(string='Renew Rejected Reason', copy=False, readonly=1,
                                        help="Renew rejected reason")
    date_request = fields.Date(string='Requested Date', required=True, track_visibility='always', readonly=True,
                               help="Requested date",
                               states={'draft': [('readonly', False)]}, default=datetime.now().strftime('%Y-%m-%d'))
    employee = fields.Many2one('hr.employee', string='Employee', required=True, readonly=True, help="Employee",
                               default=lambda self: self.env.user.employee_id.id,
                               states={'draft': [('readonly', False)]})
    purpose = fields.Char(string='Reason', track_visibility='always', required=True, readonly=True, help="Reason",
                          states={'draft': [('readonly', False)]})
    custody_name = fields.Many2one('custody.property', string='Property', required=True, readonly=True,
                                   help="Property name",
                                   states={'draft': [('readonly', False)]}
                                   )
    return_date = fields.Date(string='Return Date', required=True, track_visibility='always', readonly=True,
                              help="Return date",
                              states={'draft': [('readonly', False)]})
    renew_date = fields.Date(string='Renewal Return Date', track_visibility='always',
                             help="Return date for the renewal", readonly=True, copy=False)
    notes = fields.Html(string='Notes')
    renew_return_date = fields.Boolean(default=False, copy=False)
    renew_reject = fields.Boolean(default=False, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'Waiting For Approval'), ('approved', 'Approved'),
                              ('returned', 'Returned'), ('rejected', 'Refused')], string='Status', default='draft',
                             track_visibility='always')
    mail_send = fields.Boolean(string="Mail Send")


class HrPropertyName(models.Model):
    """
            Hr property creation model.
            """
    _name = 'custody.property'
    _description = 'Property Name'

    name = fields.Char(string='Property Name', required=True)
    image = fields.Image(string="Image",
                         help="This field holds the image used for this provider, limited to 1024x1024px")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of this provider. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of this provider. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    desc = fields.Html(string='Description', help="Description")
    company_id = fields.Many2one('res.company', 'Company', help="Company",
                                 default=lambda self: self.env.user.company_id)
    property_selection = fields.Selection([('empty', 'No Connection'),
                                           ('product', 'Products')],
                                          default='empty',
                                          string='Property From', help="Select the property")

    product_id = fields.Many2one('product.product', string='Product', help="Product")


    # def _compute_read_only(self):
    #     """ Use this function to check weather the user has the permission to change the employee"""
    #     res_user = self.env['res.users'].search([('id', '=', self._uid)])
    #     print(res_user.has_group('hr.group_hr_user'))
    #     if res_user.has_group('hr.group_hr_user'):
    #         self.read_only = True
    #     else:
    #         self.read_only = False


    @api.onchange('product_id')
    def onchange_product(self):
        self.name = self.product_id.name


class HrReturnDate(models.TransientModel):
    """Hr custody contract renewal wizard"""
    _name = 'wizard.return.date'
    _description = 'Hr Custody Name'

    returned_date = fields.Date(string='Renewal Date', required=1)

    # renewal date validation
    @api.constrains('returned_date')
    def validate_return_date(self):
        context = self._context
        custody_obj = self.env['hr.custody'].search([('id', '=', context.get('custody_id'))])
        if self.returned_date <= custody_obj.date_request:
            raise ValidationError('Please Give Valid Renewal Date')

    def proceed(self):
        context = self._context
        custody_obj = self.env['hr.custody'].search([('id', '=', context.get('custody_id'))])
        custody_obj.write({'renew_return_date': True,
                           'renew_date': self.returned_date,
                           'state': 'to_approve'})
