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


class SettlementReason(models.Model):
    """Model to define reasons for employee settlements in HR operations.
        This class stores the settlement reason and an optional description
        to provide more details about the reason."""
    _name = 'settlement.reason'
    _rec_name = 'settlement_reason'
    _description = 'Settlement Reason'

    settlement_reason = fields.Char(string="Reason", required=True,
                                    help="Reason for settlement")
    description = fields.Text(string="Description",
                              help="Description for settlement")
