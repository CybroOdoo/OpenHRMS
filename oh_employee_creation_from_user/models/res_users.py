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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import api, models


class ResUsers(models.Model):
    """Inherit res.users to automate employee creation for internal users."""
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically generate an employee record
        for internal users. Portal and public share users are excluded."""
        users = super().create(vals_list)
        for user in users:
            # Check user.share: skip portal and public share users
            if user.share or not user.has_group('base.group_user'):
                continue
            # Only create an employee if user has no existing employee record
            if not user.employee_ids:
                employee_vals = {
                    'name': user.name,
                    'user_id': user.id,
                    'company_id': user.company_id.id,
                    'work_contact_id': user.partner_id.id,
                    'work_email': user.email,
                    'work_phone': user.phone,
                }
                if user.partner_id.street:
                    employee_vals['private_street'] = user.partner_id.street
                if user.partner_id.city:
                    employee_vals['private_city'] = user.partner_id.city
                if user.partner_id.country_id:
                    employee_vals['private_country_id'] = (
                        user.partner_id.country_id.id
                    )
                if user.partner_id.phone:
                    employee_vals['private_phone'] = user.partner_id.phone
                if user.partner_id.email:
                    employee_vals['private_email'] = user.partner_id.email
                if user.image_1920:
                    employee_vals['image_1920'] = user.image_1920
                self.env['hr.employee'].sudo().create(employee_vals)
        return users
