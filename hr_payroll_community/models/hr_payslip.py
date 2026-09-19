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
import re
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import babel

# This will generate 16th of days
ROUNDING_FACTOR = 16


class HrPayslip(models.Model):
    """Create new model for getting total Payroll Sheet for an Employee"""
    _name = 'hr.payslip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Pay Slip'

    struct_id = fields.Many2one(comodel_name='hr.payroll.structure',
                                string='Structure',
                                help='Defines the rules that have to be applied'
                                     ' to this payslip, accordingly '
                                     'to the contract chosen. If you let empty '
                                     'the field contract, this field isn\'t '
                                     'mandatory anymore and thus the rules '
                                     'applied will be all the rules set on the '
                                     'structure of all contracts of the '
                                     'employee valid for the chosen period')
    name = fields.Char(string='Payslip Name', help="Enter Payslip Name")
    number = fields.Char(string='Reference', copy=False,
                         help="References for Payslip", )
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  required=True, tracking=True,
                                  help="Choose Employee for Payslip")
    date_from = fields.Date(string='Date From', required=True,
                            help="Start date for Payslip",
                            default=lambda self: fields.Date.to_string(
                                date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', required=True,
                          help="End date for Payslip",
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1,
                                                              days=-1)).date()))
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('done', 'Validated'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft', tracking=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is confirmed then status is set to \'Validated\'.
                \n* Once payment has been made the status is set to \'Paid\'.
                \n* When user cancels the payslip the status is \'Canceled\'.""")
    line_ids = fields.One2many('hr.payslip.line',
                               'slip_id',
                               string='Payslip Lines',
                               help="Choose Payslip for line")

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company.id
    )
    worked_days_line_ids = fields.One2many('hr.payslip.worked.days',
                                           'payslip_id',
                                           string='Payslip Worked Days',
                                           copy=True,
                                           help="Payslip worked days for line")
    input_line_ids = fields.One2many('hr.payslip.input',
                                     'payslip_id',
                                     string='Payslip Inputs',
                                     help="Choose Payslip Input")
    paid = fields.Boolean(string='Made Payment Order',
                          copy=False, help="Is Payment Order")
    note = fields.Text(string='Internal Note', help="Description for Payslip")
    contract_id = fields.Many2one('hr.version', string='Contract',
                                  help="Choose Contract for Payslip")
    details_by_salary_rule_category_ids = fields.One2many(
        comodel_name='hr.payslip.line',
        compute='_compute_details_by_salary_rule_category_ids',
        string='Details by Salary Rule Category', help="Details from the salary"
                                                       " rule category")
    credit_note = fields.Boolean(string='Credit Note', default=False,
                                 help="Indicates this payslip has "
                                      "a refund of another")
    payslip_run_id = fields.Many2one('hr.payslip.run',
                                     string='Payslip Batches',
                                     copy=False, help="Choose Payslip Run")
    payslip_count = fields.Integer(compute='_compute_payslip_count',
                                   string="Payslip Computation Details",
                                   help="Set Payslip Count")
    is_send_mail = fields.Boolean(
        string="Is Send Mail",
        help="Checks the Mail is send or not")
    
    basic_wage = fields.Monetary(compute='_compute_wages', string='Basic Wage')
    gross_wage = fields.Monetary(compute='_compute_wages', string='Gross Wage')
    net_wage = fields.Monetary(compute='_compute_wages', string='Net Wage')
    employer_cost = fields.Monetary(compute='_compute_wages', string='Employer Cost')
    currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)

    @property
    def paid_amount(self):
        """
        Property exposing the computed net paid amount based on worked days.
        This provides a unified monetary value for salary rules to consume.
        """
        return self._get_paid_amount()

    def _get_paid_amount(self):
        """
        Computes the total paid amount by summing the monetary values of all 
        worked day lines in this payslip.
        @return: float representing the total paid amount
        """
        self.ensure_one()
        return sum(line.amount for line in self.worked_days_line_ids)

    @api.model
    def _get_payroll_days(self, contract, date_from, date_to, total_days=30.0):
        """
        Hook to return the number of days in the payroll period.
        Can be overridden by localization modules (e.g. to use calendar days, fixed 30 days, or working days).
        """
        return total_days or 30.0

    @api.model
    def _get_contract_wage(self, contract):
        """
        Retrieves the base wage from the specified contract.
        @param contract: hr.contract record
        @return: float representing the base contract wage
        """
        return contract.wage

    @api.model
    def _get_daily_rate(self, contract, date_from, date_to, total_days=30.0):
        """Calculate the daily wage rate for an employee.

        @param contract: hr.version record
        @param date_from: Start date of the period
        @param date_to: End date of the period
        @param total_days: Total days in the payroll period (defaults to 30.0)
        @return: float representing daily rate
        """
        payroll_days = self._get_payroll_days(contract, date_from, date_to, total_days)
        if payroll_days:
            return self._get_contract_wage(contract) / payroll_days
        return 0.0

    @api.model
    def _is_paid_worked_day(self, worked_day_dict):
        """
        Determines if a worked day should be paid.
        Default: based on hr.work.entry.type 'is_paid' field.
        """
        code = worked_day_dict.get('code')
        if not code:
            return True
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', code)], limit=1)
        if work_entry_type:
            return work_entry_type.is_paid
        # Fallback if no matching work entry type is found
        # In hr_payroll_community, leaves without a code default to 'GLOBAL' and were historically deducted.
        if code == 'GLOBAL':
            return False
        return True

    @api.model
    def _compute_worked_day_amount(self, worked_day_dict, contract, date_from, date_to, total_days=30.0):
        """Compute the monetary amount for a worked day line.

        Calculates amount as daily rate multiplied by the number of days if the worked day is paid.

        @param worked_day_dict: Dictionary containing worked day details
        @param contract: hr.version record
        @param date_from: Start date of the period
        @param date_to: End date of the period
        @param total_days: Total days in the payroll period
        @return: float representing the computed monetary amount
        """
        if self._is_paid_worked_day(worked_day_dict):
            daily_rate = self._get_daily_rate(contract, date_from, date_to, total_days)
            return daily_rate * worked_day_dict.get('number_of_days', 0.0)
        return 0.0

    @api.model
    def _prepare_worked_day_line(self, worked_day_dict, contract, date_from, date_to, total_days=30.0):
        """
        Hook to process each worked day dictionary before it is finalized.
        Calculates and injects the monetary 'amount' based on the daily rate.
        @param worked_day_dict: Dictionary containing worked day data
        @param contract: hr.contract record
        @param date_from: Start date of the period
        @param date_to: End date of the period
        @param total_days: Total payroll days in the period
        @return: updated worked_day_dict with monetary 'amount'
        """
        worked_day_dict['amount'] = self._compute_worked_day_amount(worked_day_dict, contract, date_from, date_to, total_days)
        return worked_day_dict

    @api.depends('line_ids.total')
    def _compute_wages(self):
        """
        Computes the basic, gross, net, and employer cost totals for the payslip
        by dynamically summing the appropriate computed payslip lines based on 
        category codes ('BASIC', 'GROSS', 'NET', 'COMP').
        """
        def _name_has_word(line, word):
            """Match `word` as a whole word in the line's name (case-insensitive),
            not merely as a substring -- avoids e.g. 'Internet Allowance'
            being mistaken for a 'Net' line just because it contains 'net'."""
            return bool(re.search(r'\b%s\b' % re.escape(word), line.name.lower()))

        for payslip in self:
            payslip.basic_wage = sum(payslip.line_ids.filtered(lambda l: l.category_id.code == 'BASIC' or l.code == 'BASIC').mapped('total'))

            gross_lines = payslip.line_ids.filtered(lambda l: l.category_id.code == 'GROSS' or l.code == 'GROSS' or _name_has_word(l, 'gross'))
            payslip.gross_wage = sum(gross_lines.mapped('total')) if gross_lines else payslip.basic_wage

            payslip.net_wage = sum(payslip.line_ids.filtered(lambda l: l.category_id.code == 'NET' or l.code == 'NET' or _name_has_word(l, 'net')).mapped('total'))

            comp_lines = payslip.line_ids.filtered(lambda l: l.category_id.code == 'COMP' or l.code == 'COMP' or _name_has_word(l, 'employer') or _name_has_word(l, 'company'))
            payslip.employer_cost = sum(comp_lines.mapped('total'))

    @api.depends('line_ids', 'line_ids.category_id', 'line_ids.total')
    def _compute_details_by_salary_rule_category_ids(self):
        """Compute function for Salary Rule Category for getting
         all Categories"""
        for payslip in self:
            payslip.details_by_salary_rule_category_ids = payslip.mapped(
                'line_ids').filtered(lambda line: line.category_id)

    def _compute_payslip_count(self):
        """Compute function for getting Total count of Payslips"""
        for payslip in self:
            payslip.payslip_count = len(payslip.line_ids)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Function for adding constrains for payslip datas
        by considering date_from and date_to fields"""
        if any(self.filtered(
                lambda payslip: payslip.date_from > payslip.date_to)):
            raise ValidationError(
                _("Payslip 'Date From' must be earlier 'Date To'."))

    def action_payslip_draft(self):
        """Function for change stage of Payslip"""
        return self.write({'state': 'draft'})

    def action_mark_as_paid(self):
        """Mark payslip as paid"""
        return self.write({'state': 'paid'})

    def action_payslip_done(self):
        """Function for change stage of Payslip"""
        self.action_compute_sheet()
        
        send_payslip_by_email = self.env['ir.config_parameter'].sudo().get_bool(
            'send_payslip_by_email')
        if send_payslip_by_email:
            self.write({'is_send_mail': True})
        
        res = self.write({'state': 'done'})
        
        if send_payslip_by_email:
            template = self.env.ref(
                'hr_payroll_community.email_template_payslip',
                raise_if_not_found=False)
            for payslip in self:
                employee = payslip.employee_id
                recipient_email = (employee.work_email
                                    or employee.private_email
                                    or employee.work_contact_id.email)
                if template and recipient_email:
                    template.sudo().send_mail(payslip.id, force_send=True)
        return res

    def action_payslip_send(self):
        """Opens a window to compose an email,
        with template message loaded by default"""
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup(
                'hr_payroll_community.email_template_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hr.payslip',
            'default_res_ids': self.ids,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_ids': self.employee_id.work_contact_id.ids,
            'force_email': True,
        }
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_payslip_cancel(self):
        """Function for change stage of Payslip"""
        return self.write({'state': 'cancel'})

    def action_refund_sheet(self):
        """Function for refund the Payslip sheet"""
        copied_payslips = self.env['hr.payslip']
        for payslip in self:
            copied_payslip = payslip.copy(
                {'credit_note': True, 'name': _('Refund: ') + payslip.name})
            copied_payslip.action_compute_sheet()
            copied_payslips |= copied_payslip
        formview_ref = self.env.ref('hr_payroll_community.hr_payslip_view_form',
                                    False)
        treeview_ref = self.env.ref('hr_payroll_community.hr_payslip_view_tree',
                                    False)
        if len(copied_payslips) == 1:
            return {
                'name': _("Refund Payslip"),
                'view_mode': 'form',
                'res_model': 'hr.payslip',
                'res_id': copied_payslips.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
        
        return {
            'name': _("Refund Payslips"),
            'view_mode': 'list,form',
            'view_id': False,
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslips.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'list'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    def unlink(self):
        """Prevent deletion of payslips that are not in Draft or Canceled state."""
        if any(self.filtered(
                lambda payslip: payslip.state not in ('draft', 'cancel'))):
            raise UserError(
                _('You cannot delete a payslip which is not draft or cancelled!'
                  ))
        return super(HrPayslip, self).unlink()

    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date_field
        @param date_to: date_field
        @return: returns the ids of all the contracts for the given employee
        that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to),
                    ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to),
                    ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the
        # date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|',
                    ('date_end', '=', False), ('date_end', '>=', date_to)]

        clause_final = [('employee_id', '=', employee.id), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.version'].search(clause_final).ids

    def action_compute_sheet(self):
        """Compute the payslip lines and generate the payslip reference number."""
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code(
                'salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be
            # for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                           self.get_contract(payslip.employee_id,
                                             payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in
                     self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
        return True

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        Computes and returns the worked days data for the given contracts and dates.
        Evaluates the resource calendar, leaves, and standard working hours to generate
        a list of dictionaries that will be used to create hr.payslip.worked_days records.
        
        @param contracts: Recordset of hr.contract
        @param date_from: String representing start date
        @param date_to: String representing end date
        @return: List of dictionaries containing worked days values
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(
                lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from),
                                        time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to),
                                      time.max)
            calendar = contract.resource_calendar_id
            employee = contract.employee_id

            # compute worked days
            work_data = employee._get_work_days_data_batch(
                day_from, day_to, calendar=calendar)[employee.id]
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }
            res.append(attendances)

            # compute leave days, grouped by leave/work entry type
            leave_work_entry_types = self.env['resource.calendar.leaves'].search([
                ('resource_id', '=', employee.resource_id.id),
                ('count_as', '=', 'absence'),
                ('date_from', '<=', day_to),
                ('date_to', '>=', day_from),
            ]).work_entry_type_id
            for work_entry_type in leave_work_entry_types:
                leave_data = employee._get_leave_days_data_batch(
                    day_from, day_to, calendar=calendar,
                    domain=[('work_entry_type_id', '=', work_entry_type.id),
                            ('count_as', '=', 'absence')],
                )[employee.id]
                if not leave_data['hours']:
                    continue
                res.append({
                    'name': work_entry_type.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': work_entry_type.code or 'GLOBAL',
                    'number_of_days': leave_data['days'],
                    'number_of_hours': leave_data['hours'],
                    'contract_id': contract.id,
                })

        contracts_dict = {c.id: c for c in contracts}
        
        # Group dicts by contract to calculate total working days generated
        contract_days = {}
        for d in res:
            cid = d.get('contract_id')
            if cid:
                contract_days[cid] = contract_days.get(cid, 0.0) + d.get('number_of_days', 0.0)

        for worked_day_dict in res:
            contract_id = worked_day_dict.get('contract_id')
            contract = contracts_dict.get(contract_id)
            if contract:
                total_days = contract_days.get(contract_id, 30.0)
                self._prepare_worked_day_line(worked_day_dict, contract, date_from, date_to, total_days)
                
        return res

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        Gathers required manual input lines based on the salary rules attached to the contract's structure.
        
        @param contracts: Recordset of hr.contract
        @param date_from: Start date
        @param date_to: End date
        @return: List of dictionaries representing manual input line templates
        """
        res = []
        structure_ids = contracts.get_all_structures()
        rule_ids = self.env['hr.payroll.structure'].browse(
            structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in
                           sorted(rule_ids, key=lambda x: x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped(
            'input_ids')
        for contract in contracts:
            for input in inputs:
                input_data = {
                    'name': input.name,
                    'code': input.code,
                    'contract_id': contract.id,
                    'date_from': date_from,
                    'date_to': date_to,
                }
                res.append(input_data)
        return res

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        """
        The core salary engine execution loop. 
        It evaluates the salary structure, compiles the python sandbox (`localdict`) 
        containing worked days, inputs, and previous rule evaluations, and computes 
        the final monetary amount for each salary rule.
        
        @param contract_ids: List of contract IDs
        @param payslip_id: ID of the current payslip being evaluated
        @return: List of dictionaries representing computed payslip lines
        """

        def _sum_salary_rule_category(localdict, category, amount):
            """Function for getting total sum of Salary Rule Category"""
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict,
                                                      category.parent_id,
                                                      amount)
            localdict['categories'].dict[category.code] \
                = category.code in localdict[
                'categories'].dict and localdict['categories'].dict[
                      category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            """Class for Browsable Object"""

            def __init__(self, employee_id, dict, env):
                """Function for getting employee_id,dict and env"""
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                """Function for return dict"""
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for
            usability purposes"""

            def sum(self, code, from_date, to_date=None):
                """Function for getting sum of Payslip with respect to
                 from_date,to_date fields"""
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = 
                    pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date,
                                        code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for
            usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                """Function for getting sum of Payslip days with respect to
                 from_date,to_date fields"""
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, 
                    sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = 
                    pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date,
                                        code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                """Function for getting sum of Payslip with respect to
                 from_date,to_date fields"""
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                """Function for getting sum of Payslip hours with respect to
                 from_date,to_date fields"""
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for
            usability purposes"""

            def __getattr__(self, attr):
                """Attribute access delegating to the underlying payslip object."""
                try:
                    return getattr(self.dict, attr)
                except AttributeError:
                    return super().__getattr__(attr)

            def sum(self, code, from_date, to_date=None):
                """Function for getting sum of Payslip with respect to
                 from_date,to_date fields"""
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note IS NOT TRUE
                then (pl.total) else (-pl.total) end)
                FROM hr_payslip as hp, hr_payslip_line as pl
                WHERE hp.employee_id = %s AND hp.state = 'done'
                AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id 
                = pl.slip_id AND pl.code = %s""",
                                    (
                                        self.employee_id, from_date, to_date,
                                        code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten
        # by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line
        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict,
                                 self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
        baselocaldict = {'categories': categories, 'rules': rules,
                         'payslip': payslips, 'worked_days': worked_days,
                         'inputs': inputs}
        # get the ids of the structures on the contracts and their
        # parent id as well
        contracts = self.env['hr.version'].browse(contract_ids)
        if payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        elif len(contracts) == 1 and payslip.contract_id.contract_template_id.struct_id:
            structure_ids = list(
                set(payslip.contract_id.contract_template_id.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        # get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(
            structure_ids).get_all_rules()
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in
                           sorted(rule_ids, key=lambda x: x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)
        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee,
                             contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if rule._satisfy_condition(
                        localdict) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[
                        rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in
                    # the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(
                        localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in
                                  rule._recursive_search_of_rules()]
        return list(result_dict.values())


    def onchange_employee_id(self, date_from, date_to, employee_id=False,
                             contract_id=False):
        """
        Onchange handler for employee selection (legacy method, mainly used in older UI views).
        Automatically fetches the relevant contract, salary structure, worked days, 
        and input lines for the selected employee within the given period.
        """
        # defaults
        res = {
            'value': {
                'line_ids': [],
                'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
                'worked_days_line_ids': [(2, x,) for x in
                                         self.worked_days_line_ids.ids],
                'name': '',
                'contract_id': False,
                'struct_id': False,
            }
        }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        employee = self.env['hr.employee'].browse(employee_id)
        locale = self.env.context.get('lang') or 'en_US'
        res['value'].update({
            'name': _('Salary Slip of %s for %s') % (
                employee.name,
                babel.dates.format_date(date=ttyme, format='MMMM-y',
                                        locale=locale)),
            'company_id': employee.company_id.id,
        })
        if not self.env.context.get('contract'):
            # fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                # set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                # if we don't give the contract, then the input to fill
                # should be for all current contracts of the employee
                contract_ids = self.get_contract(employee, date_from, date_to)
        if not contract_ids:
            return res
        contract = self.env['hr.version'].browse(contract_ids[0])
        res['value'].update({
            'contract_id': contract.id
        })
        struct = contract.struct_id or contract.contract_template_id.struct_id or contract.structure_type_id.default_struct_id
        if not struct:
            return res
        res['value'].update({
            'struct_id': struct.id,
        })
        # computation of the salary input
        contracts = self.env['hr.version'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from,
                                                         date_to)
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        return res

    @api.onchange('employee_id', )
    def onchange_employee(self):
        """Function for getting contract for employee"""
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
            employee.name,
            babel.dates.format_date(date=ttyme, format='MMMM-y',
                                    locale=locale))
        self.company_id = employee.company_id
        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.version'].browse(contract_ids[0])
            self.struct_id = self.contract_id.struct_id or self.contract_id.contract_template_id.struct_id or self.contract_id.structure_type_id.default_struct_id
            if not self.struct_id:
                return
        if self.contract_id:
            contract_ids = self.contract_id.ids
        # computation of the salary input
        contracts = self.env['hr.version'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from,
                                                         date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        self.input_line_ids = self._merge_input_lines(input_line_ids)
        return

    @api.onchange('contract_id')
    def onchange_contract_id(self):
        """Function for getting structure when changing contract"""
        if not self.contract_id:
            self.struct_id = False
        self.with_context(contract=True).onchange_employee()
        return

    def _merge_input_lines(self, new_input_dicts):
        """Merge freshly generated "Other Inputs" line templates with the
        lines already on the payslip, preserving any amount the user has
        already typed in for a given input code instead of wiping it back
        to zero every time the employee/date onchange fires."""
        existing_by_code = {
            line.code: line.amount for line in self.input_line_ids
            if line.code
        }
        input_lines = self.input_line_ids.browse([])
        for r in new_input_dicts:
            r = dict(r)
            if r.get('code') in existing_by_code:
                r['amount'] = existing_by_code[r['code']]
            input_lines += input_lines.new(r)
        return input_lines

    def get_salary_line_total(self, code):
        """Function for getting total salary line"""
        self.ensure_one()
        line = self.line_ids.filtered(lambda line: line.code == code)
        if line:
            return line[0].total
        else:
            return 0.0

    @api.onchange('date_from')
    def onchange_date_from(self):
        """Recompute worked day lines and input lines when date_from changes."""
        if not self.date_from or not self.date_to:
            return
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []
        if self.contract_id:
            contract_ids = self.contract_id.ids
        # computation of the salary input
        contracts = self.env['hr.version'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from,
                                                         date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        self.input_line_ids = self._merge_input_lines(input_line_ids)
        if self.line_ids.search([('name', '=', 'Meal Voucher')]):
            self.line_ids.search(
                [('name', '=', 'Meal Voucher')]).salary_rule_id.write(
                {'quantity': self.worked_days_line_ids.number_of_days})
        return

    @api.onchange('date_to')
    def onchange_date_to(self):
        """Recompute worked day lines and input lines when date_to changes."""
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []
        if self.contract_id:
            contract_ids = self.contract_id.ids
        # computation of the salary input
        contracts = self.env['hr.version'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from,
                                                         date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        self.input_line_ids = self._merge_input_lines(input_line_ids)
        if self.line_ids.search([('name', '=', 'Meal Voucher')]):
            self.line_ids.search(
                [('name', '=', 'Meal Voucher')]).salary_rule_id.write(
                {'quantity': self.worked_days_line_ids.number_of_days})
        return
