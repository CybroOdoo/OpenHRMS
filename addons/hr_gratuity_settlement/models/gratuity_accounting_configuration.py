# -- coding: utf-8 --
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
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
###################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GratuityAccountingConfiguration(models.Model):
    _name = 'hr.gratuity.accounting.configuration'
    _rec_name = 'name'
    _description = "Gratuity Accounting Configuration"

    name = fields.Char(copy=False)
    active = fields.Boolean(default=True)
    gratuity_start_date = fields.Date(string='Start Date', help="Starting date of the gratuity")
    gratuity_end_date = fields.Date(string='End Date', help="Ending date of the gratuity")
    gratuity_credit_account = fields.Many2one('account.account', help="Credit account for the gratuity")
    gratuity_debit_account = fields.Many2one('account.account', help="Debit account for the gratuity")
    gratuity_journal = fields.Many2one('account.journal', help="Journal for the gratuity")
    config_contract_type = fields.Selection(
        [('limited', 'Limited'),
         ('unlimited', 'Unlimited')], default="limited", required=True,
        string='Contract Type')
    gratuity_configuration_table = fields.One2many('gratuity.configuration',
                                                   'gratuity_accounting_configuration_id')

    @api.onchange('gratuity_start_date', 'gratuity_end_date')
    def onchange_date(self):
        """ Function to check date """
        if self.gratuity_start_date and self.gratuity_end_date:
            if not self.gratuity_start_date < self.gratuity_end_date:
                raise UserError(_("Invalid date configuration!"))

    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Gratuity configuration name should be unique!')]

