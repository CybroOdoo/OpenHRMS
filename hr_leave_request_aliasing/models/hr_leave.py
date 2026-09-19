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
from odoo import api, models
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
        msg_subject = msg_dict.get('subject', '')
        mail_from = msg_dict.get('email_from', '')
        subject = re.search(self.env['ir.config_parameter'].sudo(
        ).get_str('hr_holidays.alias_prefix', ''), msg_subject)
        from_mail = re.search(self.env['ir.config_parameter'].sudo(
        ).get_str('hr_holidays.alias_domain', ''), mail_from)
        if subject and from_mail:
            email_address = email_split(msg_dict.get('email_from', False))[
                0]
            employee = self.env['hr.employee'].sudo().search(
                ['|', ('work_email', 'ilike', email_address),
                 ('user_id.email', 'ilike', email_address)], limit=1)
            msg_body = msg_dict.get('body', '')
            cleaner = re.compile('<.*?>')
            clean_msg_body = re.sub(cleaner, '', msg_body)
            date_list = re.findall(r'\d{2}/\d{2}/\d{4}', clean_msg_body)
            if len(date_list) > 0:
                start_date = datetime.strptime(
                    date_list[0], '%d/%m/%Y')
                if len(date_list) == 1:
                    date_to = start_date
                else:
                    date_to = datetime.strptime(
                        date_list[1], '%d/%m/%Y')
                no_of_days_temp = (
                        datetime.strptime(str(date_to),
                                          "%Y-%m-%d %H:%M:%S") -
                        datetime.strptime(str(start_date),
                                          '%Y-%m-%d %H:%M:%S')).days
                leave_type = self.env['hr.work.entry.type'].sudo().search([
                    ('requires_allocation', '=', False),
                    ('country_id', 'in', self.env.companies.country_id.ids + [False])
                ], limit=1)
                custom_values.update({
                    'name': msg_subject.strip(),
                    'employee_id': employee.id if employee else False,
                    'request_date_from': start_date.date(),
                    'request_date_to': date_to.date(),
                })
                if leave_type:
                    custom_values['work_entry_type_id'] = leave_type.id
        record = super(HrLeave, self.with_context(leave_fast_create=True)).message_new(msg_dict, custom_values)
        
        # Manually add followers (since leave_fast_create skips it)
        record_sudo = record.sudo()
        record_sudo.add_follower(record.employee_id.id)
        if record.validation_type == 'manager':
            record_sudo.message_subscribe(partner_ids=record.employee_id.leave_manager_id.partner_id.ids)
        elif record.validation_type == 'hr' or record.validation_type == 'both':
            record_sudo.message_subscribe(partner_ids=record._get_responsible_for_approval().partner_id.ids)
            
        return record
