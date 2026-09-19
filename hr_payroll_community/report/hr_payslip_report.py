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
from odoo import fields, models, tools


class HrPayslipReport(models.Model):
    """Create a new model for getting monthly report"""
    _name = 'hr.payslip.report'
    _description = 'Payslip Monthly Report'
    _auto = False

    name = fields.Many2one('hr.employee', string='Employee',
                           help="Choose Employee")
    date_from = fields.Date(string='From', help="Starting Date for Report")
    date_to = fields.Date(string='To', help="Ending Date for Report")
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Validated'), ('paid', 'Paid'),
         ('cancel', 'Canceled')],
        string='Status', help="Select Status for Report")
    job_id = fields.Many2one('hr.job', string='Job Title',
                             help="Choose Hr Job")
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Choose Company")
    department_id = fields.Many2one('hr.department',
                                    string='Department',
                                    help="Choose Hr Department")
    rule_name_id = fields.Many2one('hr.salary.rule.category',
                                string="Rule Category",
                                help="Choose Salary Rule Category")
    rule_amount = fields.Float(
        string="Amount", aggregator=None,
        help="Amount of a single payslip line. Not summable as a pivot "
             "measure: since this report has one row per rule line, "
             "summing it across an employee/period mixes raw components "
             "with rollup lines like Gross/Net and double- or "
             "triple-counts the same money. Use Basic/Gross/Net Salary "
             "instead for meaningful totals.")
    basic_wage = fields.Float(string="Basic Salary",
                              help="Amount of the BASIC salary rule line")
    gross_wage = fields.Float(string="Gross Salary",
                              help="Amount of the GROSS salary rule line")
    net_wage = fields.Float(string="Net Salary",
                            help="Amount of the NET salary rule line")
    travel_wage = fields.Float(string="Travel Allowance",
                               help="Amount of the Travel salary rule line")
    other_wage = fields.Float(string="Other Allowance",
                              help="Amount of the Other salary rule line")
    medical_wage = fields.Float(string="Medical Allowance",
                                help="Amount of the Medical salary rule line")
    meal_wage = fields.Float(string="Meal Allowance",
                             help="Amount of the Meal salary rule line")
    da_wage = fields.Float(string="Dearness Allowance",
                           help="Amount of the DA salary rule line")
    ca_wage = fields.Float(string="Conveyance Allowance",
                           help="Amount of the CA salary rule line")
    cagg_wage = fields.Float(string="Conveyance Allowance For Gravie",
                             help="Amount of the CAGG salary rule line")
    ma_wage = fields.Float(string="Meal Voucher",
                           help="Amount of the MA salary rule line")
    sale_wage = fields.Float(string="Sales Commission",
                             help="Amount of the SALE salary rule line")
    struct_id = fields.Many2one('hr.payroll.structure',
                                string="Salary Structure",
                                help="Choose Hr Payroll Structure")
    rule_id = fields.Many2one('hr.salary.rule',
                              string="Salary Rule", help="Choose Salary Rule")

    def _select(self):
        """Construct the SELECT clause for the report view.

        One row per payslip line (psl.id is used as the report's unique
        id) so that amounts are never summed/collapsed across unrelated
        rule lines by the SQL view itself. basic_wage/gross_wage/net_wage
        only carry a value on the line that actually matches that rule
        code, so a pivot can safely SUM them per employee/period without
        double-counting BASIC/GROSS/NET into each other.
        """
        select_str = """
            psl.id as id, ps.id as slip_id, ps.number, emp.id as name,
            dp.id as department_id, jb.id as job_id, cmp.id as company_id,
            ps.date_from, ps.date_to, ps.state as state,
            rl.id as rule_name_id, psl.total as rule_amount,
            case when rlu.code = 'BASIC' then psl.total else 0.0 end as basic_wage,
            case when rlu.code = 'GROSS' then psl.total else 0.0 end as gross_wage,
            case when rlu.code = 'NET' then psl.total else 0.0 end as net_wage,
            case when rlu.code = 'Travel' then psl.total else 0.0 end as travel_wage,
            case when rlu.code = 'Other' then psl.total else 0.0 end as other_wage,
            case when rlu.code = 'Medical' then psl.total else 0.0 end as medical_wage,
            case when rlu.code = 'Meal' then psl.total else 0.0 end as meal_wage,
            case when rlu.code = 'DA' then psl.total else 0.0 end as da_wage,
            case when rlu.code = 'CA' then psl.total else 0.0 end as ca_wage,
            case when rlu.code = 'CAGG' then psl.total else 0.0 end as cagg_wage,
            case when rlu.code = 'MA' then psl.total else 0.0 end as ma_wage,
            case when rlu.code = 'SALE' then psl.total else 0.0 end as sale_wage,
            ps.struct_id as struct_id, rlu.id as rule_id
            """
        return select_str

    def _from(self):
        """Construct the FROM clause for the report view."""
        from_str = """
                hr_payslip_line psl
                join hr_payslip ps on ps.id=psl.slip_id
                join hr_salary_rule rlu on rlu.id = psl.salary_rule_id
                join hr_employee emp on ps.employee_id=emp.id
                left join hr_version ver on ver.id=ps.contract_id
                left join hr_salary_rule_category rl on rl.id = psl.category_id
                left join hr_department dp on dp.id = ver.department_id
                left join hr_job jb on jb.id = ver.job_id
                join res_company cmp on cmp.id=ps.company_id
             """
        return from_str

    def _where(self):
        """Construct the WHERE clause.

        Cancelled payslips are voided records, not real payroll -- they
        must never contribute to Basic/Gross/Net/Employer Cost totals,
        and there is no way for a user to filter them back in (the search
        view only offers Draft/Done), so they are excluded unconditionally
        here rather than left for a report filter to (fail to) catch.
        """
        return "WHERE ps.state != 'cancel'"

    def _group_by(self):
        """No aggregation: each report row maps 1:1 to a payslip line."""
        return ""

    def init(self):
        """Initialize the view by executing the SQL query to create it."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( SELECT
                   %s
                   FROM %s
                   %s
                   %s
                   )""" % (
            self._table, self._select(), self._from(), self._where(), self._group_by()))
