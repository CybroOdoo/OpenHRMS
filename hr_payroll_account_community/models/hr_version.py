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


class HrVersion(models.Model):
    """
    Extends the hr.version model to add accounting fields.
    
    Provides configuration for an analytic account and salary journal to be used 
    when generating payslips and journal entries for a given contract version.
    """
    _inherit = 'hr.version'

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account',
                                          help="Select Analytic account")
    journal_id = fields.Many2one('account.journal',
                                 string='Salary Journal',
                                 help="Journal associated with the record")
