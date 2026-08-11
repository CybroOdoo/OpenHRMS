# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    """
    Inherited model res.config.settings.
    Exposes salary advance company settings to the settings view.
    """
    _inherit = 'res.config.settings'

    salary_advance_enabled = fields.Boolean(
        related='company_id.salary_advance_enabled',
        readonly=False
    )
    salary_advance_max_percent = fields.Float(
        related='company_id.salary_advance_max_percent',
        readonly=False
    )
    salary_advance_max_amount = fields.Float(
        related='company_id.salary_advance_max_amount',
        readonly=False
    )
    salary_advance_min_days = fields.Integer(
        related='company_id.salary_advance_min_days',
        readonly=False
    )
    salary_advance_multiple_active = fields.Boolean(
        related='company_id.salary_advance_multiple_active',
        readonly=False
    )
    salary_advance_auto_deduct = fields.Boolean(
        related='company_id.salary_advance_auto_deduct',
        readonly=False
    )
