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
"""Employee model extension to link active insurances."""
from odoo import fields, models


class HrEmployee(models.Model):
    """Inherit hr.employee to link active insurance policies."""

    _inherit = 'hr.employee'

    insurance_ids = fields.One2many(
        'hr.insurance',
        'employee_id',
        string="Insurance", help="Active employee insurances",
        domain=[('state', '=', 'active')],
    )
