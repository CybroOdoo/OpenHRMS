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
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PropertyReturnDate(models.TransientModel):
    """Hr custody contract renewal wizard"""
    _name = 'property.return.date'
    _description = 'Property Return Date'

    returned_date = fields.Date(string='Renewal Date', required=True,
                                help='Add the Return date')

    @api.constrains('returned_date')
    def validate_return_date(self):
        """The function used to renewal date validation"""
        custody_obj = self.env['hr.custody'].search(
            [('id', '=', self._context.get('custody_id'))])
        if self.returned_date <= custody_obj.date_request:
            raise ValidationError('Please Give Valid Renewal Date')

    def proceed(self):
        """The function used to proceed
        with the renewal process for the associated custody."""
        custody_obj = self.env['hr.custody'].search(
            [('id', '=', self._context.get('custody_id'))])
        custody_obj.write({'is_renew_return_date': True,
                           'renew_date': self.returned_date,
                           'state': 'to_approve'})
