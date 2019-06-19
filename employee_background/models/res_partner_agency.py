# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerAgency(models.Model):
    _inherit = 'res.partner'

    verification_agent = fields.Boolean(string='Employee Verification agent',
                                        default=False,
                                        help="Mark it if the partner is an Employee Verification Agent")