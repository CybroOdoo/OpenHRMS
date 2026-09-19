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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ReportHrPayrollCommunityReportContributionRegister(models.AbstractModel):
    """Create new model for getting Contribution Register Report"""
    _name = 'report.hr_payroll_community.report_contributionregister'
    _description = 'Payroll Contribution Register Report'

    def _get_payslip_lines(self, register_ids, date_from, date_to):
        """Function for getting Payslip Lines to Contribution Register Report.

        Always shows every payslip line for the matching payslips, exactly
        as they appear on the original payslip - not just the lines whose
        own register_id happens to match this register.

        If the register has a Partner set, the result is further scoped to
        that specific person's payslips only (Partner here identifies the
        employee, via hr.employee.work_contact_id, whose payslips this
        register's report should cover). Registers with no Partner set
        cover every employee's payslips in the period.
        """
        result = {}
        for register in self.env['hr.contribution.register'].browse(register_ids):
            domain = [
                ('slip_id.date_from', '>=', date_from),
                ('slip_id.date_to', '<=', date_to),
                ('slip_id.state', 'in', ('done', 'paid')),
            ]
            if register.partner_id:
                domain.append(
                    ('slip_id.employee_id.work_contact_id', '=', register.partner_id.id))
            result[register.id] = self.env['hr.payslip.line'].search(
                domain, order='slip_id, sequence')
        return result

    def _build_display_items(self, lines):
        """Turn a flat, slip-ordered recordset of payslip lines into a
        display list grouped by payslip: one bold "payslip name" header
        item followed by that payslip's own lines - so the payslip name
        is printed once per group instead of being repeated on every row.
        """
        items = []
        current_slip_id = None
        for line in lines:
            if line.slip_id.id != current_slip_id:
                current_slip_id = line.slip_id.id
                items.append({
                    'is_header': True,
                    'payslip_name': line.slip_id.name,
                })
            items.append({
                'code': line.code,
                'name': line.name,
                'quantity': line.quantity,
                'amount': line.amount,
                'total': line.total,
            })
        return items

    @api.model
    def _get_report_values(self, docids, data=None):
        """Function for getting Contribution Register Values"""
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))
        register_ids = self.env.context.get('active_ids', [])
        contrib_registers = self.env['hr.contribution.register'].browse(
            register_ids)
        date_from = data['form'].get('date_from', fields.Date.today())
        date_to = data['form'].get('date_to',
                                   str(datetime.now() + relativedelta(months=+1,
                                                                      day=1,
                                                                      days=-1))[
                                   :10])
        lines_by_register = self._get_payslip_lines(register_ids, date_from, date_to)
        lines_data = {}
        for register in contrib_registers:
            lines = lines_by_register.get(register.id)
            lines_data[register.id] = self._build_display_items(lines) if lines else []
        return {
            'doc_ids': docids,
            'doc_model': 'hr.contribution.register',
            'docs': contrib_registers,
            'data': data,
            'lines_data': lines_data,
        }
