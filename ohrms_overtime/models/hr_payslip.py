# -- coding: utf-8 --
################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import api, fields, models


class HrPayslip(models.Model):
    """ Extend 'hr.payslip' model to include overtime records in the
        input tree."""
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime',
                                    string='Overtime',
                                    help="Overtime records associated with this"
                                         "payslip.")

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """ function used for writing overtime record in payslip
        input tree."""
        res = super(HrPayslip, self).get_inputs(contracts, date_to, date_from)
        overtime_type = self.env.ref('ohrms_overtime.hr_salary_rule_overtime')
        contract = self.contract_id
        overtime_id = self.env['hr.overtime'].search(
            [('employee_id', '=', self.employee_id.id),
             ('contract_id', '=', self.contract_id.id),
             ('state', '=', 'approved'), ('is_payslip_paid', '=', False)])

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
        """ function used for marking paid overtime request."""
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.is_payslip_paid = True
        return super(HrPayslip, self).action_payslip_done()
