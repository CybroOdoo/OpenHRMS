# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class HrPayslipLine(models.Model):
    """Create new model for adding Payslip Line"""
    _name = 'hr.payslip.line'
    _inherit = 'hr.salary.rule'
    _description = 'Payslip Line'
    _order = 'contract_id, sequence'

    slip_id = fields.Many2one('hr.payslip', string='Pay Slip',
                              required=True,
                              ondelete='cascade',
                              help="Choose Payslip for line")
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule',
                                     required=True,
                                     help="Choose Salary Rule for line")
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True,
                                  help="Choose Employee for line")
    contract_id = fields.Many2one('hr.contract', string='Contract',
                                  required=True, index=True,
                                  help="Choose Contract for line")
    rate = fields.Float(string='Rate (%)', help="Set Rate for payslip",
                        digits=dp.get_precision('Payroll Rate'), default=100.0)
    amount = fields.Float(digits=dp.get_precision('Payroll'), string="Amount",
                          help="Set Amount for line")
    quantity = fields.Float(digits=dp.get_precision('Payroll'), default=1.0,
                            string="Quantity", help="Set Qty for line")
    total = fields.Float(compute='_compute_total', string='Total',
                         help="Total amount for Payslip",
                         digits=dp.get_precision('Payroll'), store=True)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        """Function for compute total amount"""
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model_create_multi
    def create(self, vals_list):
        """Function for change value at the time of creation"""
        for values in vals_list:
            if 'employee_id' not in values or 'contract_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get(
                    'employee_id') or payslip.employee_id.id
                values['contract_id'] = (values.get(
                    'contract_id') or payslip.contract_id and
                                         payslip.contract_id.id)
                if not values['contract_id']:
                    raise UserError(
                        _('You must set a contract to create a payslip line.'))
        return super(HrPayslipLine, self).create(vals_list)
