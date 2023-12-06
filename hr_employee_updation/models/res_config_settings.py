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


class ResConfigSettings(models.TransientModel):
    """Inherited the res_config_settings to add notice_period
    configurations."""
    _inherit = 'res.config.settings'

    notice_period = fields.Boolean(string='Notice Period',
                                   help='Enable to configure a notice period'
                                        ' for an employee.')
    no_of_days = fields.Integer(string='Notice Period Days',
                                help='Set the number of days for the notice'
                                     ' period.')

    def set_values(self):
        """Save the configuration values for notice period in the system."""
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "hr_resignation.notice_period", self.notice_period)
        self.env['ir.config_parameter'].sudo().set_param(
            "hr_resignation.no_of_days", self.no_of_days)

    @api.model
    def get_values(self):
        """Retrieve the configuration values for notice period from the
         system."""
        res = super().get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['notice_period'] = get_param('hr_resignation.notice_period')
        res['no_of_days'] = int(get_param('hr_resignation.no_of_days'))
        return res
