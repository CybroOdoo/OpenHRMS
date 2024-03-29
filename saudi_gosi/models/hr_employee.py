# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from datetime import date

from odoo import fields, models


class Gosi(models.Model):
    """This class calculate whether the employee is eligible for the GOSI
    contribution"""
    _inherit = 'hr.employee'

    type = fields.Selection([('saudi', 'Saudi')], string='Type',
                            help="Select the type")
    gosi_number = fields.Char(string='GOSI Number', help="Gosi Number")
    issue_date = fields.Date(string='Issued Date', help="Issued Date")
    age = fields.Char(string='Age',compute='_compute_age', help="Age")
    limit = fields.Boolean(string='Eligible For GOSI', default=False,
                           readonly=True, help='Whether the Employee is'
                                               ' eligible for the GOSI')

    def _compute_age(self):
        """This function is used to compute the age of the employee according
        to the given date of birth and also identify whether the employee is
         eligible for the GOSI(The age of employee should be between 18 and
         60)"""
        for res in self:
            if res.birthday:
                age = ((date.today()-res.birthday)/365).days
                res.age = age
                if int(res.age) <= 60 and int(res.age) >= 18:
                    res.limit = True
                else:
                    res.limit = False
            else:
                res.age = 0
                res.limit = False
