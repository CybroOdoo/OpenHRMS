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
from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime')

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(PayslipOverTime, self).get_inputs(contracts, date_to, date_from)
        overtime_type = self.env.ref('ohrms_overtime.hr_salary_rule_overtime')
        contract = self.contract_id
        overtime_id = self.env['hr.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                      ('contract_id', '=', self.contract_id.id),
                                                      ('state', '=', 'approved'), ('payslip_paid', '=', False)])
        hrs_amount = overtime_id.mapped('cash_hrs_amount')
        day_amount = overtime_id.mapped('cash_day_amount')
        cash_amount = sum(hrs_amount) + sum(day_amount)
        if overtime_id:
            self.overtime_ids = overtime_id
            input_data = {
                'name': overtime_type.name,
                'code': overtime_type.code,
                'amount': cash_amount,
                'contract_id': contract.id,
            }
            res.append(input_data)
        return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = True
        return super(PayslipOverTime, self).action_payslip_done()
