# -*- coding: utf-8 -*-
import datetime
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError,UserError
date_format = "%Y-%m-%d"


class OtherSettlements(models.Model):
    _name = 'other.settlements'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Settlement"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
    ], default='draft', track_visibility='onchange')

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    employee_name = fields.Many2one('hr.employee', string='Employee', required=True)
    joined_date = fields.Date(string="Joined Date")
    worked_years = fields.Integer(string="Total Work Years")
    last_month_salary = fields.Integer(string="Last Salary", required=True, default=0)
    allowance = fields.Char(string="Dearness Allowance", default=0)
    gratuity_amount = fields.Integer(string="Gratuity Payable", required=True, default=0, readony=True, help=("Gratuity is calculated based on 							the equation Last salary * Number of years of service * 15 / 26 "))

    reason = fields.Many2one('settlement.reason', string="Settlement Reason", required="True")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('other.settlements')
        return super(OtherSettlements, self).create(vals)

    # Check whether any Settlement request already exists
    @api.onchange('employee_name')
    @api.depends('employee_name')
    def check_request_existence(self):
        for rec in self:
            if rec.employee_name:
                settlement_request = self.env['other.settlements'].search([('employee_name', '=', rec.employee_name.id),
                                                                           ('state', 'in', ['draft', 'validate', 'approve'])])
                if settlement_request:

                    raise ValidationError(_('A Settlement request is already processed'
                                                ' for this employee'))

    @api.multi
    def validate_function(self):
        # calculating the years of work by the employee
        worked_years = int(datetime.datetime.now().year) - int(str(self.joined_date).split('-')[0])

        if worked_years >= 1:

            self.worked_years = worked_years

            cr = self._cr  # find out the correct  date of last salary of  employee
            query = """select amount from hr_payslip_line psl 
                       inner join hr_payslip ps on ps.id=psl.slip_id
                       where ps.employee_id="""+str(self.employee_name.id)+\
                       """and ps.state='done' and psl.code='NET' 
                       order by ps.date_from desc limit 1"""

            cr.execute(query)
            data = cr.fetchall()
            if data:
                 last_salary = data[0][0]
            else:
                last_salary = 0

            self.last_month_salary = last_salary

            amount = ((self.last_month_salary + int(self.allowance)) * int(worked_years) * 15) / 26
            self.gratuity_amount = round(amount) if self.state == 'approve' else 0

            self.write({
                'state': 'validate'})
        else:

            self.write({
                'state': 'draft'})
            self.worked_years = worked_years

            raise exceptions.except_orm(_('Employee Working Period is less than 1 Year'),
                                  _('Only an Employee with minimum 1 years of working, will get the Settlement advantage'))

    def approve_function(self):

        if not self.allowance.isdigit() :
            raise ValidationError(_('Allowance value should be numeric !!'))

        self.write({
            'state': 'approve'
        })

        amount = ((self.last_month_salary + int(self.allowance)) * int(self.worked_years) * 15) / 26
        self.gratuity_amount = round(amount) if self.state == 'approve' else 0

    def cancel_function(self):
        self.write({
            'state': 'cancel'
        })

    def draft_function(self):
        self.write({
            'state': 'draft'
        })

class SettlementReason(models.Model):
    _name = 'settlement.reason'
    _rec_name = 'settlement_reason'


    settlement_reason = fields.Char(string="Reason",required=True)
    description = fields.Text(string="Description")