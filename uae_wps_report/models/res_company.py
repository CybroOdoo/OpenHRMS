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


class Company(models.Model):
    """
        Extends the 'res.company' model to include additional fields and
        override default methods for company-specific functionality.
    """
    _inherit = 'res.company'

    employer_id = fields.Char(string="Employer ID", help="Company Employer ID")

    def write(self, vals):
        """
            Overrides the default write method to ensure that the company
            registry and employer ID fields are properly formatted before
            updating the record.
         """
        if 'company_registry' in vals:
            vals['company_registry'] = vals[
                'company_registry'].zfill(13) if vals[
                'company_registry'] else False
        if 'employer_id' in vals:
            vals['employer_id'] = vals[
                'employer_id'].zfill(13) if vals['employer_id'] else False
        return super().write(vals)

    @api.model
    def create(self, vals):
        """
            Overrides the default create method to ensure that the company
            registry and employer ID fields are properly formatted before
            creating the record.
        """
        vals['company_registry'] = vals[
            'company_registry'].zfill(13) if vals['company_registry'] else False
        if 'employer_id' in vals:
            vals['employer_id'] = vals[
                'employer_id'].zfill(13) if vals['employer_id'] else False
        return super().create(vals)
