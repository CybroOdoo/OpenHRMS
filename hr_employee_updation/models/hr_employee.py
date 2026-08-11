# -*- coding: utf-8 -*-
#############################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
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
from datetime import timedelta
from odoo import api, fields, models, _

GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female'),
                    ('other', 'Other')]


class HrEmployee(models.Model):
    """Extended model for HR employees with additional features."""
    _inherit = 'hr.employee'

    personal_mobile = fields.Char(string='Mobile', related='private_phone',
                                  help="Personal mobile number of the "
                                       "employee", store=True, )
    joining_date = fields.Date(compute='_compute_joining_date',
                               string='Joining Date', store=True,
                               help="Employee joining date computed from the"
                                    " contract start date")
    id_expiry_date = fields.Date(help='Expiry date of Identification document',
                                 string='Expiry Date',)
    identification_attachment_ids = fields.Many2many(
        'ir.attachment', 'id_attachment_rel',
        'id_ref', 'attach_ref', string="Attachment",
        help='Attach the copy of Identification document')
    passport_attachment_ids = fields.Many2many(
        'ir.attachment',
        'passport_attachment_rel',
        'passport_ref', 'attach_ref1', string="Attachment",
        help='Attach the copy of Passport')
    family_info_ids = fields.One2many('hr.employee.family', 'employee_id',
                                      string='Family',
                                      help='Family Information')

    @api.depends('version_id')
    def _compute_joining_date(self):
        """Compute the joining date of the employee based on their contract
         information."""
        for employee in self:
            employee.joining_date = min(
                employee.version_id.mapped('date_start')) \
                if employee.version_id else False

    @api.onchange('spouse_complete_name', 'spouse_birthdate')
    def _onchange_spouse_complete_name(self):
        """Populates the family_info_ids field with the spouse's information,
         creating a family member record associated with the employee when
         spouse's complete name or birthdate changed."""
        relation = self.env.ref('hr_employee_updation.employee_relationship')
        if self.spouse_complete_name and self.spouse_birthdate:
            self.family_info_ids = [(0, 0, {
                'member_name': self.spouse_complete_name,
                'relation_id': relation.id,
                'birth_date': self.spouse_birthdate,
            })]

    def expiry_mail_reminder(self):
        """Sending  ID and Passport expiry notification."""
        current_date = fields.Date.context_today(self)
        employee_ids = self.search(['|', ('id_expiry_date', '!=', False),
                                    ('passport_expiration_date', '!=', False)])
        for employee in employee_ids:
            if employee.id_expiry_date:
                id_days = int(self.env['ir.config_parameter'].sudo().get_param('hr_employee_updation.id_expiry_days', 14))
                exp_date = fields.Date.from_string(
                    employee.id_expiry_date) - timedelta(days=id_days)
                if current_date == exp_date:
                    mail_content = ("Hello  " + employee.name + ",<br>Your ID "
                                    + (employee.identification_id or '') +
                                    " is going to expire on " +
                                    str(employee.id_expiry_date)
                                    + ". Please renew it before expiry date")
                    main_content = {
                        'subject': _('ID-%s Expired On %s') % (
                            employee.identification_id or '',
                            employee.id_expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': employee.work_email or employee.private_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()
            if employee.passport_expiration_date:
                passport_days = int(self.env['ir.config_parameter'].sudo().get_param('hr_employee_updation.passport_expiry_days', 180))
                exp_date = fields.Date.from_string(
                    employee.passport_expiration_date) - timedelta(days=passport_days)
                if current_date == exp_date:
                    mail_content = ("  Hello  " + employee.name +
                                    ",<br>Your Passport " + (employee.passport_id or '')
                                    +" is going to expire on " +
                                    str(employee.passport_expiration_date) +
                                    ". Please renew it before expire")
                    main_content = {
                        'subject': _('Passport-%s Expired On %s') % (
                            employee.passport_id or '',
                            employee.passport_expiration_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': employee.work_email or employee.private_email,
                    }
                    self.env['mail.mail'].sudo().create(main_content).send()

    def action_send_manual_reminder_id(self):
        """Manually send ID expiry notification to the employee."""
        for employee in self:
            if not employee.id_expiry_date:
                continue
            mail_content = ("Hello  " + employee.name + ",<br>This is a reminder that your ID "
                            + (employee.identification_id or '') +
                            " is going to expire on " +
                            str(employee.id_expiry_date)
                            + ". Please renew it before expiry date")
            main_content = {
                'subject': _('Reminder: ID-%s Expiring On %s') % (
                    employee.identification_id or '',
                    employee.id_expiry_date),
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': employee.work_email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()
        return True

    def action_send_manual_reminder_pass(self):
        """Manually send Passport expiry notification to the employee."""
        for employee in self:
            if not employee.passport_expiration_date:
                continue
            mail_content = ("Hello  " + employee.name +
                            ",<br>This is a reminder that your Passport " + (employee.passport_id or '')
                            +" is going to expire on " +
                            str(employee.passport_expiration_date) +
                            ". Please renew it before expire")
            main_content = {
                'subject': _('Reminder: Passport-%s Expiring On %s') % (
                    employee.passport_id or '',
                    employee.passport_expiration_date),
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': employee.work_email,
            }
            self.env['mail.mail'].sudo().create(main_content).send()
        return True
