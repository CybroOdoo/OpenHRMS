# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SalaryAdvancePaymentWizard(models.TransientModel):
    """
    Transient model for the salary advance payment wizard.
    Allows HR Officers and Accounting staff to register payments for approved salary advances.
    """
    _name = 'salary.advance.payment.wizard'
    _description = 'Register Salary Advance Payment'

    advance_id = fields.Many2one('salary.advance', string='Salary Advance', required=True,
                                 help="The salary advance record this payment is for.")
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True,
                               help="The date the payment is made.")
    payment_reference = fields.Char(string='Payment Reference',
                                    help="A reference for the payment, such as a check number.")
    payment_memo = fields.Char(string='Memo',
                               help="An internal note or memo for the payment journal entry.")
    amount = fields.Monetary(string='Payment Amount', related='advance_id.advance', readonly=True,
                             help="The total amount to be paid.")
    currency_id = fields.Many2one('res.currency', related='advance_id.currency_id',
                                  help="The currency of the payment.")

    def action_register_payment(self):
        """
        Creates and posts an account.payment record for the salary advance.
        Links the created payment to the advance record and updates its state to 'paid'.
        """
        self.ensure_one()
        advance = self.advance_id
        company = advance.company_id

        if not advance.journal_id or not advance.receivable_account_id:
            raise UserError(_('Please configure the Payment Journal and Employee Advance Account on the advance record before registering a payment.'))
            
        payment_method_line = advance.journal_id.outbound_payment_method_line_ids[:1]
        if not payment_method_line:
            raise UserError(_('The selected payment journal must have at least one outbound payment method configured.'))

        # Create account.payment
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'payment_method_line_id': payment_method_line.id,
            'memo': self.payment_reference or advance.name,
            'journal_id': advance.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': advance.employee_id.work_contact_id.id or advance.employee_id.user_id.partner_id.id,
            'destination_account_id': advance.receivable_account_id.id,
        }
        
        # Partner is required for account.payment in Odoo.
        if not payment_vals['partner_id']:
            raise UserError(_('The employee must have a related Work Contact or User configured to register a payment.'))

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # Link payment to advance
        advance.payment_ids = [(4, payment.id)]
        
        # Advance state to paid
        advance.state = 'paid'
        
        return {'type': 'ir.actions.act_window_close'}
