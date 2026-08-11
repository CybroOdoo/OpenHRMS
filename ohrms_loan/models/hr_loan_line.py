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


class HrLoanLine(models.Model):
    """ Model for managing details of loan request installments"""
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True,
                       help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee",
                                  help="Employee")
    principal_amount = fields.Float(string="Principal Amount", help="Principal Amount")
    interest_amount = fields.Float(string="Interest Amount", help="Interest Amount")
    amount = fields.Float(string="Amount", required=True, help="Amount", compute='_compute_amount', store=True, readonly=False)

    @api.depends('principal_amount', 'interest_amount')
    def _compute_amount(self):
        """
        Compute the total amount for the installment line by adding the
        principal amount and the interest amount.
        """
        for line in self:
            if line.principal_amount or line.interest_amount:
                line.amount = line.principal_amount + line.interest_amount

    @api.depends('date', 'amount')
    def _compute_display_name(self):
        """
        Compute the display name for the installment line, formatted as
        'Month DD, YYYY (CurrencySymbolAmount)'.
        """
        for line in self:
            date_str = line.date.strftime('%B %d, %Y') if line.date else 'Unknown Date'
            # Format amount according to currency if possible, or just standard format
            currency = line.loan_id.currency_id.symbol if line.loan_id and line.loan_id.currency_id else '$'
            line.display_name = f"{date_str} ({currency}{line.amount:,.2f})"

    paid = fields.Boolean(string="Paid", help="Indicates whether the "
                                              "installment has been paid.")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.",
                              help="Reference to the associated loan.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.",
                                 help="Reference to the associated "
                                      "payslip, if any.")

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method to restrict the addition of installment
        lines to an approved loan, unless triggered by early settlement.
        """
        lines = super(HrLoanLine, self).create(vals_list)
        for line in lines:
            if line.loan_id.state == 'approve' and not self.env.context.get('early_settlement'):
                raise UserError(_("You cannot add installment lines to an approved loan."))
        return lines

    def write(self, vals):
        """
        Override the write method to restrict modifications to installment lines
        of an approved loan. Only 'paid' and 'payslip_id' fields can be updated
        during standard processing. Also sends an email notification when paid.
        """
        for line in self:
            if line.loan_id.state == 'approve' and not self.env.context.get('early_settlement') and not self.env.context.get('loan_deferment'):
                # Allow updates to 'paid' and 'payslip_id' from payslip processing
                allowed_fields = {'paid', 'payslip_id'}
                if any(field not in allowed_fields for field in vals):
                    raise UserError(_("You cannot modify installment lines of an approved loan."))
                    
        res = super(HrLoanLine, self).write(vals)
        
        if 'paid' in vals and vals['paid']:
            for line in self:
                template = self.env.ref('ohrms_loan.email_template_loan_installment_paid', raise_if_not_found=False)
                if template:
                    email_to = line.employee_id.work_email or (line.employee_id.user_id.email if line.employee_id.user_id else '') or ''
                    if email_to:
                        template.send_mail(line.id, force_send=True, email_values={'email_to': email_to})
                    
        return res

    def unlink(self):
        """
        Override the unlink method to restrict the deletion of installment
        lines from an approved loan, unless triggered by early settlement.
        """
        for line in self:
            if line.loan_id.state == 'approve' and not self.env.context.get('early_settlement'):
                raise UserError(_("You cannot delete installment lines from an approved loan."))
        return super(HrLoanLine, self).unlink()
