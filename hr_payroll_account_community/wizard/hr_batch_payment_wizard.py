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
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrBatchPaymentWizard(models.TransientModel):
    """
    Wizard for processing mass payroll payments.
    
    Allows HR managers to select a batch of confirmed payslips and 
    automatically generate outbound payments in a specified journal, 
    reconciling them against the net wage liability lines.
    """
    _name = 'hr.batch.payment.wizard'
    _description = 'Batch Payment Wizard'

    company_id = fields.Many2one('res.company', compute='_compute_company_and_currency', store=False)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method', required=True,
                                             domain="[('journal_id', '=', journal_id), ('payment_type', '=', 'outbound')]")
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.context_today)
    payslip_ids = fields.Many2many('hr.payslip', string='Payslips', required=True)
    amount = fields.Monetary(string='Amount', compute='_compute_amount_memo')
    memo = fields.Char(string='Memo', compute='_compute_amount_memo')
    currency_id = fields.Many2one('res.currency', compute='_compute_company_and_currency')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Recipient Bank Account')

    @api.depends('payslip_ids')
    def _compute_amount_memo(self):
        """Compute the total amount and memo/reference for the batch payment."""
        for wizard in self:
            if wizard.payslip_ids:
                wizard.amount = sum(wizard.payslip_ids.mapped('net_wage'))
                if len(wizard.payslip_ids) == 1:
                    wizard.memo = wizard.payslip_ids[0].number
                else:
                    wizard.memo = _("Batch Payment: %s Payslips") % len(wizard.payslip_ids)
            else:
                wizard.amount = 0.0
                wizard.memo = False

    @api.depends('payslip_ids')
    def _compute_company_and_currency(self):
        """Compute the company and currency based on the selected payslips."""
        for wizard in self:
            if wizard.payslip_ids:
                wizard.company_id = wizard.payslip_ids[0].company_id.id
                wizard.currency_id = wizard.payslip_ids[0].company_id.currency_id.id
            else:
                wizard.company_id = self.env.company.id
                wizard.currency_id = self.env.company.currency_id.id

    @api.model
    def default_get(self, fields_list):
        """
        Populate default fields from context.
        
        Reads active_id(s) from context (either hr.payslip or hr.payslip.run)
        to pre-fill the selected payslips and determine the default journal.
        """
        res = super(HrBatchPaymentWizard, self).default_get(fields_list)
        payslip_ids = []
        if self.env.context.get('active_model') == 'hr.payslip.run':
            run_id = self.env.context.get('active_id')
            if run_id:
                run = self.env['hr.payslip.run'].browse(run_id)
                payslip_ids = run.slip_ids.ids
                res['payslip_ids'] = [(6, 0, payslip_ids)]
        elif self.env.context.get('active_model') == 'hr.payslip':
            payslip_ids = self.env.context.get('active_ids', [])
            res['payslip_ids'] = [(6, 0, payslip_ids)]
            
        if payslip_ids:
            payslip = self.env['hr.payslip'].browse(payslip_ids[0])
            company_id = payslip.company_id.id
            res['company_id'] = company_id
            res['currency_id'] = payslip.company_id.currency_id.id
            
            # Find a default journal for this specific company
            journal = self.env['account.journal'].search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', company_id)
            ], limit=1)
            if journal:
                res['journal_id'] = journal.id
        return res

    def action_create_payment(self):
        """
        Generate and post payments for the selected payslips.
        
        Iterates over the payslips, finds the appropriate payable accounting line 
        (matching the NET salary rule or fallback), and creates an outbound payment.
        Reconciles the payment with the payslip's move line.
        """
        self.ensure_one()
        payslips = self.payslip_ids.filtered(lambda p: p.state == 'done' and p.move_id)
        if not payslips:
            raise UserError(_("There are no confirmed payslips with accounting entries selected."))

        payments_created = self.env['account.payment']
        
        # Get the NET salary rule to definitively know the correct payable account
        net_rule = self.env['hr.salary.rule'].search([('code', '=', 'NET')], limit=1)
        net_account_id = net_rule.account_credit_id.id if net_rule else False

        for slip in payslips:
            # We strictly only want to pay the NET salary liability to the employee.
            # Other credit lines (like taxes, loans, or misconfigured GROSS rules) should NOT be paid out via this wizard.
            payable_lines = slip.move_id.line_ids.filtered(
                lambda l: l.account_id.reconcile 
                and not l.reconciled and l.credit > 0
            )
            
            # 1. Try to find the exact line generated by the NET rule
            target_lines = payable_lines.filtered(lambda l: l.account_id.id == net_account_id) if net_account_id else self.env['account.move.line']
            
            # 2. Fallback: Find lines that exactly match the net wage amount
            if not target_lines:
                target_lines = payable_lines.filtered(
                    lambda l: slip.company_id.currency_id.compare_amounts(l.credit, slip.net_wage) == 0
                )
                
            # 3. Last resort fallback
            if not target_lines and payable_lines:
                target_lines = payable_lines[0]
                
            if not target_lines:
                continue
                
            # Pick exactly ONE line to act as the primary Net Salary line to pay
            line = target_lines[0]
            
            partner_id = line.partner_id.id or slip.employee_id.work_contact_id.id
            if not partner_id:
                raise UserError(_("No partner found for employee %s. Please configure the Private Address on the employee form.") % slip.employee_id.name)
            
            # Create the payment strictly capped at the net wage
            payment_amount = line.credit if line.credit <= slip.net_wage else slip.net_wage
            
            payment_vals = {
                'date': self.payment_date,
                'amount': payment_amount,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': partner_id,
                'destination_account_id': line.account_id.id,
                'journal_id': self.journal_id.id,
                'payment_method_line_id': self.payment_method_line_id.id,
                'memo': slip.number,
                'company_id': line.company_id.id,
            }
            payment = self.env['account.payment'].with_company(line.company_id).create(payment_vals)
            payment.action_post()
            payments_created |= payment
            
            # Reconcile the payment with the payslip's payable line
            payment_lines = payment.move_id.line_ids.filtered(
                lambda l: l.account_id == line.account_id and not l.reconciled
            )
            if payment_lines:
                (line + payment_lines).reconcile()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
