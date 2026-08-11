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
from markupsafe import Markup

class HrLoanTopup(models.TransientModel):
    """
    Wizard for processing a top-up on an existing loan.
    Allows adding an additional principal amount to an approved loan, and optionally
    extending the loan term by adding more installments.
    """
    _name = 'hr.loan.topup'
    _description = 'Loan Top-Up Wizard'

    loan_id = fields.Many2one('hr.loan', string="Loan", required=True)
    topup_amount = fields.Float(string="Top-Up Amount", required=True, help="Additional amount to add to the existing loan.")
    additional_installments = fields.Integer(string="Additional Installments", default=0, help="Optional: Number of extra months to extend the loan term.")

    def action_topup(self):
        """
        Process the top-up by increasing the loan principal and optionally the 
        installment count, then recalculating the remaining schedule while
        preserving the existing paid lines.
        """
        self.ensure_one()
        if self.topup_amount <= 0:
            raise UserError(_("Top-Up Amount must be strictly positive."))
            
        loan = self.loan_id
        
        # 1. Add top-up amount to loan amount
        old_amount = loan.loan_amount
        loan.loan_amount += self.topup_amount
        
        # 2. Add additional installments
        if self.additional_installments > 0:
            loan.installment += self.additional_installments
            
        # 3. Restructure the schedule safely
        # We pass early_settlement=True in context to bypass the block on unlinking/creating lines
        loan.with_context(early_settlement=True).action_compute_installment()
        
        # 4. Trigger Accounting Entry if available
        if hasattr(loan, 'action_topup_accounting'):
            loan.action_topup_accounting(self.topup_amount)
            
        # 5. Log action in chatter
        msg = Markup(_(
            "<b>Loan Top-Up Processed</b><br/>"
            "An additional amount of <b>%s</b> has been added to the loan.<br/>"
            "The loan principal was increased from %s to %s.<br/>"
            "The future schedule has been automatically recalculated."
        )) % (self.topup_amount, old_amount, loan.loan_amount)
        loan.message_post(body=msg)
        
        return {'type': 'ir.actions.act_window_close'}
