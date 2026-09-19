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


class DocumentType(models.Model):
    """This model is used to categorize and manage various document
     types in the system."""
    _name = 'document.type'
    _description = 'Document Type'

    name = fields.Char(string="Name", required=True,
                       help="Name of the document type")
    before_days = fields.Integer(string="Days Before",
                                 help="How many number of days before to get "
                                      "the notification email.")
    notification_type = fields.Selection([
        ('single', 'Notification on expiry date'),
        ('multi', 'Notification before few days'),
        ('everyday', 'Everyday till expiry date'),
        ('everyday_after', 'Notification on and after expiry')
    ], string='Notification Type',
        help="Select type of the documents expiry notification.")
