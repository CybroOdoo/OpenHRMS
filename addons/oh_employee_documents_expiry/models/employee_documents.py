# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, AccessError
from collections import defaultdict


class HrEmployeeDocument(models.Model):
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'

    def mail_reminder(self):
        """Sending document expiry notification to employees."""

        date_now = fields.Date.today()
        match = self.search([])
        for i in match:
            if i.expiry_date:
                if i.notification_type == 'single':
                    exp_date = fields.Date.from_string(i.expiry_date)
                    print('exp_date :', exp_date)
                    if date_now == i.expiry_date:
                        mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + " is going to expire on " + \
                                       str(i.expiry_date) + ". Please renew it before expiry date"
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                i.name, i.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': i.employee_ref.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                elif i.notification_type == 'multi':
                    exp_date = fields.Date.from_string(
                        i.expiry_date) - timedelta(days=i.before_days)
                    if date_now == exp_date or date_now == i.expiry_date:  # on Expire date and few days(As it set) before expire date
                        mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + \
                                       " is going to expire on " + str(
                            i.expiry_date) + \
                                       ". Please renew it before expiry date"
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                i.name, i.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': i.employee_ref.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                elif i.notification_type == 'everyday':
                    exp_date = fields.Date.from_string(
                        i.expiry_date) - timedelta(days=i.before_days)
                    if date_now >= exp_date or date_now == i.expiry_date:
                        mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + \
                                       " is going to expire on " + str(
                            i.expiry_date) + \
                                       ". Please renew it before expiry date"
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                i.name, i.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': i.employee_ref.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                elif i.notification_type == 'everyday_after':
                    exp_date = fields.Date.from_string(
                        i.expiry_date) + timedelta(days=i.before_days)
                    if date_now <= exp_date or date_now == i.expiry_date:
                        mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + \
                                       " is expired on " + str(i.expiry_date) + \
                                       ". Please renew it "
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                i.name, i.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': i.employee_ref.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()
                else:
                    exp_date = fields.Date.from_string(
                        i.expiry_date) - timedelta(days=7)
                    if date_now == exp_date:
                        mail_content = "  Hello  " + i.employee_ref.name + ",<br>Your Document " + i.name + \
                                       " is going to expire on " + \
                                       str(i.expiry_date) + ". Please renew it before expiry date"
                        main_content = {
                            'subject': _('Document-%s Expired On %s') % (
                                i.name, i.expiry_date),
                            'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': i.employee_ref.work_email,
                        }
                        self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = fields.Date.from_string(each.expiry_date)
                if exp_date < date.today():
                    raise Warning('Your Document Is Expired.')

    name = fields.Char(string='Document Number', required=True, copy=False,
                       help='You can give your'
                            'Document number.')
    description = fields.Text(string='Description', copy=False,
                              help="Description")
    expiry_date = fields.Date(string='Expiry Date', copy=False,
                              help="Date of expiry")
    employee_ref = fields.Many2one('hr.employee', invisible=1, copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel',
                                         'doc_id', 'attach_id3',
                                         string="Attachment",
                                         help='You can attach the copy of your document',
                                         copy=False)
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(),
                             help="Date of issue", copy=False)
    document_type = fields.Many2one('document.type', string="Document Type",
                                    help="Document type")
    before_days = fields.Integer(string="Days",
                                 help="How many number of days before to get the notification email")
    notification_type = fields.Selection([
        ('single', 'Notification on expiry date'),
        ('multi', 'Notification before few days'),
        ('everyday', 'Everyday till expiry date'),
        ('everyday_after', 'Notification on and after expiry')
    ], string='Notification Type',
        help="""
        Notification on expiry date: You will get notification only on expiry date.
        Notification before few days: You will get notification in 2 days.On expiry date and number of days before date.
        Everyday till expiry date: You will get notification from number of days till the expiry date of the document.
        Notification on and after expiry: You will get notification on the expiry date and continues upto Days.
        If you did't select any then you will get notification before 7 days of document expiry.""")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _document_count(self):
        for each in self:
            document_ids = self.env['hr.employee.document'].sudo().search(
                [('employee_ref', '=', each.id)])
            each.document_count = len(document_ids)

    def document_view(self):
        self.ensure_one()
        domain = [
            ('employee_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_ref': %s}" % self.id
        }

    document_count = fields.Integer(compute='_document_count',
                                    string='# Documents')


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('hr.employee.document',
                                      'doc_attachment_id', 'attach_id3',
                                      'doc_id',
                                      string="Attachment", invisible=1)
    attach_rel = fields.Many2many('hr.document', 'attach_id', 'attachment_id3',
                                  'document_id',
                                  string="Attachment", invisible=1)

    @api.model
    def check(self, mode, values=None):
        """ Restricts the access to an ir.attachment, according to referred mode """
        if self.env.is_superuser():
            return True
        # Always require an internal user (aka, employee) to access to a attachment
        if not (self.env.is_admin() or self.env.user._is_internal()):
            if not self.env.user.has_group('hr.group_hr_manager'):
                raise AccessError(
                    _("Sorry, you are not allowed to access this document."))
        # collect the records to check (by model)
        model_ids = defaultdict(set)  # {model_name: set(ids)}
        if self:
            # DLE P173: `test_01_portal_attachment`
            self.env['ir.attachment'].flush_model(
                ['res_model', 'res_id', 'create_uid', 'public', 'res_field'])
            self._cr.execute(
                'SELECT res_model, res_id, create_uid, public, res_field FROM ir_attachment WHERE id IN %s',
                [tuple(self.ids)])
            for res_model, res_id, create_uid, public, res_field in self._cr.fetchall():
                if public and mode == 'read':
                    continue
                if not self.env.is_system() and (res_field or (
                        not res_id and create_uid != self.env.uid)):
                    if not self.env.user.has_group('hr.group_hr_manager'):
                        raise AccessError(
                            _("Sorry, you are not allowed to access this document."))
                if not (res_model and res_id):
                    continue
                model_ids[res_model].add(res_id)
        if values and values.get('res_model') and values.get('res_id'):
            model_ids[values['res_model']].add(values['res_id'])

        # check access rights on the records
        for res_model, res_ids in model_ids.items():
            # ignore attachments that are not attached to a resource anymore
            # when checking access rights (resource was deleted but attachment
            # was not)
            if res_model not in self.env:
                continue
            if res_model == 'res.users' and len(
                    res_ids) == 1 and self.env.uid == list(res_ids)[0]:
                # by default a user cannot write on itself, despite the list of writeable fields
                # e.g. in the case of a user inserting an image into his image signature
                # we need to bypass this check which would needlessly throw us away
                continue
            records = self.env[res_model].browse(res_ids).exists()
            # For related models, check if we can write to the model, as unlinking
            # and creating attachments can be seen as an update to the model
            access_mode = 'write' if mode in ('create', 'unlink') else mode
            records.check_access_rights(access_mode)
            records.check_access_rule(access_mode)
