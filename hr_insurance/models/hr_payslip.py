#############################################################################
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
#############################################################################
"""Payslip extension to support employee insurance salary deductions."""
from odoo import api, models


class HrPayslip(models.Model):
    """Inherited to add insurance deduction inputs and handle deduction confirmation."""

    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        """Include active insurance deductions in payslip inputs."""
        res = super().get_inputs(contract_ids, date_from, date_to)
        contract_obj = self.env['hr.version']
        for contract in contract_ids:
            if hasattr(contract, 'employee_id'):
                emp_id = contract.employee_id
            else:
                emp_id = contract_obj.browse(contract).employee_id
            if not emp_id:
                continue

            eligible_insurances = emp_id.insurance_ids.filtered(
                lambda i: i.state == 'active' and not i.is_deducted and i.date_from <= date_to,
            )
            total_deduction = sum(ins.deducted_amount for ins in eligible_insurances)

            if total_deduction != 0:
                insur_input = next((r for r in res if r.get('code') == 'INSUR'), None)
                contract_val = contract.id if hasattr(contract, 'id') else contract
                if insur_input:
                    insur_input['amount'] = total_deduction
                else:
                    res.append({
                        'name': 'Insurance Amount',
                        'code': 'INSUR',
                        'amount': total_deduction,
                        'contract_id': contract_val,
                    })
        return res

    def action_payslip_done(self):
        """Override to mark the insurance as deducted once the payslip is done."""
        res = super().action_payslip_done()
        for slip in self:
            if any(line.code == 'INSUR' for line in slip.line_ids):
                slip_date_to = slip.date_to
                eligible_insurances = slip.employee_id.insurance_ids.filtered(
                    lambda ins, d=slip_date_to: (
                        ins.state == 'active' and not ins.is_deducted and ins.date_from <= d
                    ),
                )
                for ins in eligible_insurances:
                    ins.is_deducted = True
        return res
