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


class Company(models.Model):
    """
        Extends the 'res.company' model to include additional fields and
        override default methods for UAE WPS functionality.
    """
    _inherit = 'res.company'

    company_registry = fields.Char(
        string="Company Registry", size=13,
        help="Company Registry / Establishment Card Number (13 digits)")
    employer_id = fields.Char(
        string="Employer ID", size=13,
        help="Company Employer ID for WPS (13 digits)")
    wps_agent_id = fields.Many2one(
        'wps.agent', string="WPS Agent / Bank",
        help="Company WPS Disbursing Bank or Agent")

    def write(self, vals):
        """
            Overrides the default write method to ensure that the company
            registry and employer ID fields are properly formatted before
            updating the record.
        """
        if 'company_registry' in vals:
            val = vals['company_registry']
            vals['company_registry'] = str(val).zfill(13) if val else False
        if 'employer_id' in vals:
            val = vals['employer_id']
            vals['employer_id'] = str(val).zfill(13) if val else False
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """
            Overrides the default create method to ensure that the company
            registry and employer ID fields are properly formatted before
            creating the record.
        """
        for vals in vals_list:
            if 'company_registry' in vals:
                val = vals['company_registry']
                vals['company_registry'] = str(val).zfill(13) if val else False
            if 'employer_id' in vals:
                val = vals['employer_id']
                vals['employer_id'] = str(val).zfill(13) if val else False
        return super().create(vals_list)
