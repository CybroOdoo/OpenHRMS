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
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Inherit res_config_settings model for adding some fields in Settings"""
    _inherit = 'res.config.settings'

    module_account_accountant = fields.Boolean(string='Account Accountant',
                                               help="Is Account Accountant")
    module_l10n_fr_hr_payroll = fields.Boolean(string='French Payroll',
                                               help="Is French Payroll")
    module_l10n_be_hr_payroll = fields.Boolean(string='Belgium Payroll',
                                               help="Is Belgium Payroll")
    module_l10n_in_hr_payroll = fields.Boolean(string='Indian Payroll',
                                               help="Is Indian Payroll")
    send_payslip_by_email = fields.Boolean(
        string="Automatic Send Payslip By Mail",
        help="Is needed for automatic send mail")

    @api.model
    def get_values(self):
        """Function for getting boolean"""
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        send_payslip_by_email = params.get_bool('send_payslip_by_email',
                                                default=False)
        res.update(
            send_payslip_by_email=send_payslip_by_email
        )
        return res

    def set_values(self):
        """Function for setting boolean"""
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_bool(
            "send_payslip_by_email",
            self.send_payslip_by_email)
