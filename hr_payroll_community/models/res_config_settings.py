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

    _inherit = "res.config.settings"

    module_account_accountant = fields.Boolean(
        string="Account Accountant",
        help="Enable accountant features and accounting integration.",
    )
    module_l10n_fr_hr_payroll = fields.Boolean(
        string="French Payroll",
        help="Install the French Payroll localization module.",
    )
    module_l10n_be_hr_payroll = fields.Boolean(
        string="Belgium Payroll",
        help="Install the Belgian Payroll localization module.",
    )
    module_l10n_in_hr_payroll = fields.Boolean(
        string="Indian Payroll",
        help="Install the Indian Payroll localization module.",
    )
    send_payslip_by_email = fields.Boolean(
        string="Automatic Send Payslip By Mail",
        help="Automatically send confirmed payslips to employees via email.",
    )

    @api.model
    def get_values(self):
        """Function for getting boolean"""
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        send_payslip_by_email = params.get_bool(
            "send_payslip_by_email", default=False
        )
        res.update(send_payslip_by_email=send_payslip_by_email)
        return res

    def set_values(self):
        """Function for setting boolean"""
        res = super().set_values()
        self.env["ir.config_parameter"].sudo().set_bool(
            "send_payslip_by_email", self.send_payslip_by_email
        )
        return res
