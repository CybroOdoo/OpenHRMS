# -*- coding: utf-8 -*-
#############################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
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
from odoo import fields, models


class HrContract(models.Model):
    """This class extends the 'hr.contract' model to add a custom 'notice_days'
     field. The 'notice_days' field is used to store the notice period for HR
     contracts."""
    _inherit = 'hr.contract'

    def _default_notice_days(self):
        """Get the default notice period from the  configuration.
            :return: The default notice period in days.
            :rtype: int """
        return self.env['ir.config_parameter'].get_param(
            'hr_employee_updation.no_of_days') if self.env[
            'ir.config_parameter'].get_param(
            'hr_employee_updation.notice_period') else 0

    notice_days = fields.Integer(string="Notice Period",
                                 default=_default_notice_days,
                                 help="Number of days required for notice"
                                      " before termination.")
