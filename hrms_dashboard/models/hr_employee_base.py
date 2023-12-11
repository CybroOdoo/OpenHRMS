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
from datetime import timedelta
from odoo import models, fields


class HrEmployeeBase(models.AbstractModel):
    """Inherits the model hr.employee.base to override the
     method _compute_newly_hired"""
    _inherit = 'hr.employee.base'

    def _compute_newly_hired(self):
        new_hire_date = fields.Datetime.now() - timedelta(days=90)
        for employee in self:
            if employee['first_contract_date']:
                employee.newly_hired = (employee[
                                           'first_contract_date'] >
                                        new_hire_date.date())
            else:
                employee.newly_hired = employee[
                                           'create_date'] > new_hire_date
