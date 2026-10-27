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
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """
    Model representing configuration settings for HR Leave Request Aliasing.
    Adds alias_prefix and alias_domain fields to configure email aliases for leave requests.
    """
    _inherit = 'res.config.settings'

    alias_prefix = fields.Char(string='Prefix',
                               help='Default alias name for leave',
                               translate=True,
                               config_parameter='hr_holidays.alias_prefix')
    alias_domain = fields.Char(string='Domain', translate=True,
                               help='Default alias domain for leave',
                               config_parameter='hr_holidays.alias_domain')
