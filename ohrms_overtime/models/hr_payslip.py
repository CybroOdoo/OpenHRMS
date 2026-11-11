# -*- coding: utf-8 -*-
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
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        overtime_type = self.env.ref(
            'ohrms_overtime.hr_salary_rule_overtime', raise_if_not_found=False)
        if not overtime_type:
            return res

        for contract in contracts:
            overtime_records = self.env['hr.overtime'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('contract_id', '=', contract.id),
                ('state', '=', 'approved'),
                ('type', '=', 'cash'),
                ('is_payslip_paid', '=', False),
            ])
            if overtime_records:
                for payslip in self:
                    if payslip.employee_id == contract.employee_id:
                        payslip.overtime_ids = [(6, 0, overtime_records.ids)]
                hrs_amount = overtime_records.mapped('cash_hrs_amount')
                day_amount = overtime_records.mapped('cash_day_amount')
                cash_amount = sum(hrs_amount) + sum(day_amount)
                input_data = {
                    'name': overtime_type.name,
                    'code': overtime_type.code,
                    'amount': cash_amount,
                    'contract_id': contract.id,
                }
                res.append(input_data)
        return res

    @api.model
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        """Include overtime_ids in onchange_employee_id values."""
        res = super(HrPayslip, self).onchange_employee_id(
            date_from, date_to, employee_id=employee_id, contract_id=contract_id)
        if employee_id and 'value' in res:
            domain = [
                ('employee_id', '=', employee_id),
                ('state', '=', 'approved'),
                ('type', '=', 'cash'),
                ('is_payslip_paid', '=', False),
            ]
            cid = contract_id or res['value'].get('contract_id')
            if cid:
                domain.append(('contract_id', '=', cid))
            overtime_records = self.env['hr.overtime'].search(domain)
            if overtime_records:
                res['value']['overtime_ids'] = [(6, 0, overtime_records.ids)]
        return res

    def action_compute_sheet(self):
        """Link overtime records if not already linked when computing sheet."""
        res = super(HrPayslip, self).action_compute_sheet()
        for payslip in self:
            if not payslip.overtime_ids and payslip.employee_id:
                domain = [
                    ('employee_id', '=', payslip.employee_id.id),
                    ('state', '=', 'approved'),
                    ('type', '=', 'cash'),
                    ('is_payslip_paid', '=', False),
                ]
                if payslip.contract_id:
                    domain.append(('contract_id', '=', payslip.contract_id.id))
                overtimes = self.env['hr.overtime'].search(domain)
                if overtimes:
                    payslip.overtime_ids = [(6, 0, overtimes.ids)]
        return res

    def action_payslip_done(self):
        """ function used for marking paid overtime request."""
        res = super(HrPayslip, self).action_payslip_done()
        for payslip in self:
            overtimes = payslip.overtime_ids
            if not overtimes and payslip.employee_id:
                domain = [
                    ('employee_id', '=', payslip.employee_id.id),
                    ('state', '=', 'approved'),
                    ('type', '=', 'cash'),
                    ('is_payslip_paid', '=', False),
                ]
                if payslip.contract_id:
                    domain.append(('contract_id', '=', payslip.contract_id.id))
                overtimes = self.env['hr.overtime'].search(domain)
                if overtimes:
                    payslip.overtime_ids = [(6, 0, overtimes.ids)]
            overtimes.filtered(
                lambda r: r.type == 'cash').write({'is_payslip_paid': True})
        return res
