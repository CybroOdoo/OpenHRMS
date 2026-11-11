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


class WpsAgent(models.Model):
    """
        Model representing a UAE Wages Protection System (WPS) Agent.
        In UAE WPS, an Agent is an authorized financial institution
        (bank or exchange house) identified by a 9-digit Central Bank
        Routing Code.
    """
    _name = 'wps.agent'
    _description = 'WPS Agent / Bank'
    _order = 'name'

    name = fields.Char(string="Agent / Bank Name", required=True)
    routing_code = fields.Char(
        string="Routing Code", size=9, required=True,
        help="9-digit Central Bank Routing Code for UAE WPS"
    )

    def write(self, vals):
        """Ensure routing code is properly zero-padded to 9 digits."""
        if 'routing_code' in vals and vals['routing_code']:
            vals['routing_code'] = str(vals['routing_code']).zfill(9)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure routing code is properly zero-padded to 9 digits."""
        for vals in vals_list:
            if vals.get('routing_code'):
                vals['routing_code'] = str(vals['routing_code']).zfill(9)
        return super().create(vals_list)
