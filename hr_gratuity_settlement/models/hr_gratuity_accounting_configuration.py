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
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class HrGratuityAccountingConfiguration(models.Model):
    _name = 'hr.gratuity.accounting.configuration'
    _rec_name = 'name'
    _description = "Hr Gratuity Accounting Configuration"

    name = fields.Char(copy=False, string="Name", help="Name")
    active = fields.Boolean(default=True, string="Active", help="Is it active")
    gratuity_start_date = fields.Date(string='Start Date',
                                      help="Starting date of the gratuity")
    gratuity_end_date = fields.Date(string='End Date',
                                    help="Ending date of the gratuity")
    gratuity_credit_account_id = fields.Many2one('account.account',
                                                 string='Gratuity Credit Account',
                                                 help="Credit account for the"
                                                      " gratuity")
    gratuity_debit_account_id = fields.Many2one('account.account',
                                                string='Gratuity Debit Account',
                                                help="Debit account for the"
                                                     " gratuity")
    gratuity_journal_id = fields.Many2one('account.journal',
                                          string='Gratuity journal',
                                          help="Journal for the gratuity")
    config_contract_type = fields.Selection(
        [('limited', 'Limited'),
         ('unlimited', 'Unlimited')], default="limited", required=True,
        string='Contract Type', help="Contract type")
    gratuity_configuration_table_ids = fields.One2many('gratuity.configuration',
                                                       'gratuity_account'
                                                       'ing_configuration_id',
                                                       string='Gratuity'
                                                              'Configuration Table',
                                                       help='Configuration table')

    @api.onchange('gratuity_start_date', 'gratuity_end_date')
    def _onchange_gratuity_start_date(self):
        """ Function to check date """
        if self.gratuity_start_date and self.gratuity_end_date:
            if not self.gratuity_start_date < self.gratuity_end_date:
                raise UserError(_("Invalid date configuration!"))

    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Gratuity configuration name should be unique!')]
