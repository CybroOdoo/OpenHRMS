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
from odoo import models, api

class HrPayslip(models.Model):
    """
    Inherits the hr.payslip model to inject resignation deductions/recoveries.
    """
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """Override to inject resignation recoveries into payslip inputs automatically."""
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)

        for contract in contracts:
            # Look for active/approved resignations overlapping the payslip period
            resignation = self.env['hr.resignation'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', 'in', ['clearance', 'settlement', 'relieved']),
            ], order='id desc', limit=1)
            
            if resignation and resignation.expected_revealing_date:
                # If the revealing date falls within this payslip period, append recoveries
                if date_from <= resignation.expected_revealing_date <= date_to:
                    has_asset = False
                    for input_line in res:
                        if input_line.get('contract_id') == contract.id:
                            if input_line.get('code') == 'ASSET_REC':
                                input_line['amount'] = resignation.asset_recovery
                                has_asset = True
                    
                    # Forcefully append if they are missing from the structure
                    if not has_asset and resignation.asset_recovery:
                        res.append({
                            'name': 'Asset Recovery Input',
                            'code': 'ASSET_REC',
                            'amount': resignation.asset_recovery,
                            'contract_id': contract.id,
                        })
        return res
