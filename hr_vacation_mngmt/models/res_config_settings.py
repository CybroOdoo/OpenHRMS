# -- coding: utf-8 --
###############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Inherits the resconfig settings for adding new fields"""
    _inherit = 'res.config.settings'

    leave_reminder = fields.Boolean(string='Leave Reminder Email',
                                    config_parameter='hr_vacation_mngmt.leave_reminder',
                                    help="Enable this field send leave "
                                         "remainder emails to hr managers")
    reminder_day_before = fields.Integer(string='Reminder Day Before',
                                         config_parameter='hr_vacation_mngmt.reminder_day_before',
                                         help='Set the day to send  reminder .')
    default_leave_salary = fields.Selection([('0', 'Basic'),
                                             ('1', 'Gross')],
                                            string='Leave Salary',
                                            default_model='hr.leave',
                                            config_parameter='hr_vacation_mngmt.default_leave_salary',
                                            help='Set the default leave salary'
                                                 ' of employee.')
    expense_account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
        required=True,
        domain="[('account_type','=','expense')]",
        help="Select expense account",
        config_parameter='hr_vacation_mngmt.expense_account_id')
    expense_product_id = fields.Many2one('product.product',
                                        domain="[('type', '=', 'service')]",
                                         required=True,
                                         string="Expense Product",
                                         help="Select expense product",
                                         config_parameter='hr_vacation_mngmt.expense_product_id')
