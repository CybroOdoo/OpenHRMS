# -*- coding: utf-8 -*-
#############################################################################
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
#############################################################################
import re
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import email_split


class HrLeave(models.Model):
    """
    Model representing hr leave inheriting hr.leave to add incoming mail
    processing capabilities for creating leave requests automatically.
    """
    _inherit = 'hr.leave'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """This function extracts required fields of hr.holidays from incoming
         mail then creating records"""
        if custom_values is None:
            custom_values = {}
        msg_subject = msg_dict.get('subject', '').strip()
        emails = email_split(msg_dict.get('email_from', ''))
        email_address = emails[0].strip() if emails else ''
        alias_prefix = self.env['ir.config_parameter'].sudo().get_str(
            'hr_holidays.alias_prefix', '').strip()
        alias_domain = self.env['ir.config_parameter'].sudo().get_str(
            'hr_holidays.alias_domain', '').strip()

        subject_match = False
        domain_match = False
        if alias_prefix and alias_domain:
            prefix_pattern = rf"^{re.escape(alias_prefix)}"
            subject_match = bool(re.search(
                prefix_pattern, msg_subject, re.IGNORECASE))
            domain_pattern = rf"@{re.escape(alias_domain)}$"
            domain_match = bool(re.search(
                domain_pattern, email_address, re.IGNORECASE))

        if subject_match and domain_match:
            employee = False
            if email_address:
                employee = self.env['hr.employee'].sudo().search(
                    ['|', ('work_email', '=ilike', email_address),
                     ('user_id.email', '=ilike', email_address)], limit=1)
            msg_body = msg_dict.get('body', '')
            cleaner = re.compile(r'<.*?>')
            clean_msg_body = re.sub(cleaner, '', msg_body)

            # Check for labeled dates 'Date From: DD/MM/YYYY' and
            # 'Date To: DD/MM/YYYY'
            date_from_match = re.search(
                r'date\s*from\s*:\s*(\d{2}/\d{2}/\d{4})',
                clean_msg_body, re.IGNORECASE)
            date_to_match = re.search(
                r'date\s*to\s*:\s*(\d{2}/\d{2}/\d{4})',
                clean_msg_body, re.IGNORECASE)
            if date_from_match:
                start_date = datetime.strptime(
                    date_from_match.group(1), '%d/%m/%Y').date()
                if date_to_match:
                    date_to = datetime.strptime(
                        date_to_match.group(1), '%d/%m/%Y').date()
                else:
                    date_to = start_date
            else:
                date_list = re.findall(r'\d{2}/\d{2}/\d{4}', clean_msg_body)
                if len(date_list) > 0:
                    start_date = datetime.strptime(
                        date_list[0], '%d/%m/%Y').date()
                    if len(date_list) == 1:
                        date_to = start_date
                    else:
                        date_to = datetime.strptime(
                            date_list[1], '%d/%m/%Y').date()
                else:
                    start_date = fields.Date.context_today(self)
                    date_to = start_date
            leave_type = self.env['hr.work.entry.type'].sudo().search([
                ('requires_allocation', '=', False),
                ('country_id', 'in', self.env.companies.country_id.ids + [False]),
            ], limit=1)
            custom_values.update({
                'name': msg_subject,
                'employee_id': employee.id if employee else False,
                'request_date_from': start_date,
                'request_date_to': date_to,
            })
            if leave_type:
                custom_values['work_entry_type_id'] = leave_type.id
        record = super(
            HrLeave, self.with_context(leave_fast_create=True),
        ).message_new(msg_dict, custom_values)

        # Manually add followers (since leave_fast_create skips it)
        record_sudo = record.sudo()
        if record.employee_id:
            record_sudo.add_follower(record.employee_id.id)
            if record.validation_type == 'manager' and record.employee_id.leave_manager_id:
                record_sudo.message_subscribe(
                    partner_ids=record.employee_id.leave_manager_id.partner_id.ids)
            elif record.validation_type in ('hr', 'both'):
                responsible = record._get_responsible_for_approval()
                if responsible and responsible.partner_id:
                    record_sudo.message_subscribe(
                        partner_ids=responsible.partner_id.ids)

        return record
