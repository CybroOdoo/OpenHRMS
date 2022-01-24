# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'

    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account',
                                                domain=[('deprecated', '=', False)],
                                                help="It acts as a default account for credit amount",
                                                ondelete='restrict')
    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account',
                                               domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
                                               help="It acts as a default account for debit amount",
                                               ondelete='restrict')
