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
from odoo import models, fields


class ResCompanyPolicy(models.TransientModel):
    """Creates the model res.company.policy to display company policy in a popup."""
    _name = 'res.company.policy'
    _description = 'Company Policy'

    company_id = fields.Many2one('res.company', string="Company",
                                 default=lambda self: self.env.company,
                                 help="Company of the policy")
    policy_info = fields.Html(related='company_id.company_info',
                              string="Policy",
                              help="Information about the policy")
