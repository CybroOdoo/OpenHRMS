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
from dateutil.relativedelta import relativedelta
from markupsafe import Markup

class HrLoanDeferment(models.TransientModel):
    """ 
    Wizard for deferring a specific loan installment.
    Pushes the selected installment and all subsequent unpaid installments
    back by one month.
    """
    _name = 'hr.loan.deferment'
    _description = 'Loan Deferment Wizard'

    loan_id = fields.Many2one('hr.loan', string="Loan", required=True)
    loan_line_id = fields.Many2one(
        'hr.loan.line', 
        string="Installment to Defer", 
        required=True,
        domain="[('loan_id', '=', loan_id), ('paid', '=', False)]",
        help="Select the installment you want to pause. This and all future installments will be pushed back by one month."
    )
    reason = fields.Char(string="Reason", required=True, help="Reason for deferring the loan installment")

    def action_defer(self):
        """
        Execute the deferment process by shifting the date of the selected
        installment and all future installments ahead by one month, and log
        the action in the chatter.
        """
        self.ensure_one()
        if not self.loan_line_id:
            raise UserError(_("Please select an installment to defer."))
            
        loan = self.loan_id
        
        # Find all unpaid lines that are on or after the selected line's date
        lines_to_push = loan.loan_lines.filtered(
            lambda l: not l.paid and l.date >= self.loan_line_id.date
        )
        
        # Sort them just to be safe, though filtered keeps order usually
        for line in lines_to_push.sorted(key=lambda x: x.date):
            # Push the date exactly 1 month into the future
            line.with_context(loan_deferment=True).write({
                'date': line.date + relativedelta(months=1)
            })
            
        # Log the action in the loan chatter
        msg = Markup(_(
            "<b>Loan Installment Deferred</b><br/>"
            "An installment has been paused.<br/>"
            "<b>Reason:</b> %s<br/>"
            "All subsequent unpaid installments have been pushed back by one month."
        )) % (self.reason)
        loan.message_post(body=msg)
        
        return {'type': 'ir.actions.act_window_close'}
