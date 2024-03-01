# -*- coding: utf-8 -*-
#############################################################################

#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: ASWIN A K (odoo@cybrosys.com)
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


class Bank(models.Model):
    """
        Extends the standard Odoo 'res.bank' model to include an additional
        field for the routing code of the bank.
    """
    _inherit = 'res.bank'

    routing_code = fields.Char(
        string="Routing Code", size=9, required=True, help="Bank Route Code")

    def write(self, vals):
        """
            Overrides the default write method to ensure that the routing code
            is properly formatted before updating the record.
        """
        if 'routing_code' in vals.keys():
            vals['routing_code'] = vals['routing_code'].zfill(9)
        return super().write(vals)

    @api.model
    def create(self, vals):
        """
            Overrides the default create method to ensure that the routing code
            is properly formatted before creating the record.
        """
        vals['routing_code'] = vals['routing_code'].zfill(9)
        return super().create(vals)
