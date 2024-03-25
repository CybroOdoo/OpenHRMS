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
import datetime
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError,UserError
date_format = "%Y-%m-%d"


class EmployeeGratuity(models.Model):
    _name = 'hr.gratuity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Gratuity"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validated'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')],
        default='draft', tracking='onchange')
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.resignation', string='Employee', required=True,
                                    domain="[('state', '=', 'approved')]")
    joined_date = fields.Date(string="Joined Date", readonly=True)
    worked_years = fields.Integer(string="Total Work Years", readonly=True)
    last_month_salary = fields.Integer(string="Last Salary", required=True, default=0)
    allowance = fields.Char(string="Dearness Allowance", default=0)
    gratuity_amount = fields.Integer(string="Gratuity Payable", required=True, default=0,
                                  readony=True, help=("Gratuity is calculated based on the "
                                  "equation Last salary * Number of years of service * 15 / 26 "))
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', 'Company',  default=lambda self: self.env.user.company_id)

    # assigning the sequence for the record
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.gratuity')
        return super(EmployeeGratuity, self).create(vals)

    # Check whether any Gratuity request already exists
    @api.onchange('employee_id')
    @api.depends('employee_id')
    def check_request_existence(self):
        for rec in self:
            if rec.employee_id:

                gratuity_request = self.env['hr.gratuity'].search([('employee_id', '=', rec.employee_id.id),
                                                                   ('state', 'in', ['draft', 'validate', 'approve', 'cancel'])])
                if gratuity_request:
                    raise ValidationError(_('A Settlement request is already processed'
                                            ' for this employee'))

    
    def validate_function(self):
        # calculating the years of work by the employee
        worked_years = int(datetime.datetime.now().year) - int(str(self.joined_date).split('-')[0])

        if worked_years < 5:

            self.write({
                'state': 'draft'})

            worked_years = int(datetime.datetime.now().year) - int(str(self.joined_date).split('-')[0])
            self.worked_years = worked_years

            raise exceptions.except_orm(_('Employee Working Period is less than 5 Year'),
                                        _('Only an Employee with minimum 5 years of working, will get the Gratuity'))
        else:

            worked_years = int(datetime.datetime.now().year) - int(str(self.joined_date).split('-')[0])
            self.worked_years = worked_years

            cr = self._cr  # find out the correct  date of last salary of  employee

            query = """select amount from hr_payslip_line psl 
                       inner join hr_payslip ps on ps.id=psl.slip_id
                       where ps.employee_id="""+str(self.employee_id.employee_id.id)+\
                       """and ps.state='done' and psl.code='NET'
                       order by ps.date_from desc limit 1"""

            cr.execute(query)
            data = cr.fetchall()
            if data :
                 last_salary = data[0][0]
            else :
                last_salary = 0
            self.last_month_salary = last_salary

            amount = ((self.last_month_salary + int(self.allowance)) * int(worked_years) * 15) / 26
            self.gratuity_amount = round(amount) if self.state == 'approve' else 0

            self.write({
                'state': 'validate'})

    def approve_function(self):

        if not self.allowance.isdigit():
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

    # assigning the join date of the selected employee
    @api.onchange('employee_id')
    def _on_change_employee_id(self):
        rec = self.env['hr.resignation'].search([['id', '=', self.employee_id.id]])
        if rec:
            self.joined_date = rec.joined_date
        else:
            self.joined_date = ''
