# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import api, fields, models


class HrContract(models.Model):
    """Inherited HR Contract Model.This model extends the base 'hr.contract'
    model with an additional field 'emp_transfer' for linking to a transferred
    employee. The 'create' method is customized to handle the creation of new
    HR contract records. It also updates the state of the linked employee
    transfer record if applicable."""
    _inherit = 'hr.contract'

    emp_transfer = fields.Many2one(
        'employee.transfer', string='Transferred Employee',
        help="Employee who has been transferred")

    @api.model
    def create(self, vals):
        """Create a new HR contract record with the provided values."""
        res = super(HrContract, self).create(vals)
        if res.emp_transfer:
            res.emp_transfer.write(
                {'state': 'done'})
        return res
