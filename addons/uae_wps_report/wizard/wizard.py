# -*- coding: utf-8 -*-
from datetime import date, datetime
import pytz
import json
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from odoo.tools import date_utils, xlsxwriter, io


class Wizard(models.TransientModel):
    _name = 'wps.wizard'

    report_file = fields.Char()
    name = fields.Char(string="File Name")
    args = []
    date = fields.Datetime()
    time = fields.Datetime()
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    days = fields.Integer(string="Days of Payment", readonly=True, store=True)
    salary_month = fields.Selection([('01', 'January'),
                                     ('02', 'February'),
                                     ('03', 'March'),
                                     ('04', 'April'),
                                     ('05', 'May'),
                                     ('06', 'June'),
                                     ('07', 'July'),
                                     ('08', 'August'),
                                     ('09', 'September'),
                                     ('10', 'October'),
                                     ('11', 'November'),
                                     ('12', 'December')
                                     ], string="Month of Salary", readonly=True)

    @api.onchange('start_date', 'end_date')
    def on_date_change(self):
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            self.days = 1 + (date(year=int(end[0]), month=int(end[1]), day=int(end[2]))
                             - date(year=int(start[0]), month=int(start[1]), day=int(start[2]))).days
            if start[1] == end[1]:
                self.salary_month = start[1]

    def print_xlsx(self):
        company = self.env['res.company']._company_default_get('wps.wizard')
        if not company.company_registry:
            raise UserError(_('Please Set Company Registry Number First'))
        employees = self.env['hr.employee'].search([])
        # print(users.mapped('labour_card_number'))
        flags = {'labour_card_number': True, 'salary_card_number': True, 'agent_id': True}
        print(flags)
        for user in employees:
            if not user.labour_card_number:
                flags['labour_card_number'] = False
            if not user.salary_card_number:
                flags['salary_card_number'] = False
            if not user.agent_id:
                flags['agent_id'] = False
        if not flags['labour_card_number']:
            raise UserError(_('Please Set Labour Card Number of All Employees'))
        if not flags['salary_card_number']:
            raise UserError(_('Please Set Salary Card Number / Account Number of All Employees'))
        if not flags['agent_id']:
            raise UserError(_('Please Set Employee Card Number of All Employees'))
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            if not start[1] == end[1]:
                raise UserError(_('The Dates Can of Same Month Only'))
        slips = self.env['wps.wizard'].get_data(self.start_date, self.end_date)
        if not slips:
            raise UserError(_('There are no payslip Created for the selected month'))
        company = self.env['res.company']._company_default_get('wps.wizard')
        user = self.env['res.users'].browse(self.env.uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            date = pytz.utc.localize(datetime.now()).astimezone(tz)
            time = pytz.utc.localize(datetime.now()).astimezone(tz)
        else:
            date = datetime.now()
            time = datetime.now()
        if not company.employer_id:
            raise UserError(_('Configure Your Company Employer ID'))
        self.name = company.employer_id + date.strftime("%y%m%d%H%M%S")
        self.report_file = company.employer_id + date.strftime("%y%m%d%H%M%S")
        if not company.bank_ids:
            raise UserError(_('Configure Your Bank In Accounting Dashboard'))

        datas = {
            'context': self._context,
            'date': date,
            'time': time,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        # self.write({
        #     'date': date,
        #     'time': time
        # })
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'wps.wizard',
                     'options': json.dumps(datas, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Uae wps Report'
                     },
            'report_type': 'wps_xlsx'
        }

    def get_data(self, start, end):
        cr = self._cr
        slips = self.env['hr.payslip'].search(['&', ('date_from', '<=', start), ('date_to', '>=', end)])
        if not slips:
            return False
        ids = ''
        for slip in slips:
            if ids:
                ids = ids + ',' + str(slip.id)
            else:
                ids = ids + str(slip.id)
        language = self.env.context['lang']
        print(language)
        # net_salary = "'{\"" + language + "\": " + "\"Net Salary" + "\"}'"
        # print(net_salary, "jsonp")
        query = """select hr_employee.id,labour_card_number, salary_card_number, agent_id, hr_payslip_line.amount 
                    from hr_employee join hr_payslip_line 
                    on hr_employee.id = hr_payslip_line.employee_id 
                    where hr_payslip_line.name = (""" + "'{\"" + language + "\": " + "\"Net Salary" + "\"}'" + """) and 
                    hr_payslip_line.slip_id in(""" + ids + """) """
        cr.execute(query)
        data = cr.fetchall()
        return data

    def get_days(self, emp_id, start, end):
        slip = self.env['hr.payslip'].search(['&', ('employee_id', '=', emp_id)
                                                 , ('date_from', '=', start)
                                                 , ('date_to', '=', end)])
        days = self.env['hr.payslip.worked_days'].search([('payslip_id', '=', slip.id)])
        total_days = sum(rec.number_of_days for rec in days)

        return total_days

    def get_leaves(self, emp_id, start, end):
        leaves = self.env['hr.leave'].search(['&', ('employee_id', '=', emp_id)
                                                 , ('date_from', '>=', start)
                                                 , ('date_to', '<=', end)
                                                 , ('holiday_status_id', '=', 4)]).number_of_days
        return leaves * -1

    def get_xlsx_report(self, lines, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        format0 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('SIF Report')
        dat = self.get_data(lines['start_date'], lines['end_date'])
        if dat == 11:
            raise UserError(_('There is no payslips created for this month'))
        dat = [list(da) for da in dat]
        for da in dat:
            da[3] = self.env['res.bank'].browse(da[3]).routing_code
        count = 0
        sum = 0
        for count in range(0, len(dat)):
            days = self.get_days(dat[count][0], lines['start_date'], lines['end_date'])
            leaves = self.get_leaves(dat[count][0], lines['start_date'], lines['end_date'])
            sheet.set_column(1, 1, 14)
            sheet.set_column(2, 2, 12)
            sheet.set_column(3, 3, 16)
            sheet.set_column(4, 4, 9)
            sheet.set_column(5, 5, 9)
            sheet.write(count, 0, 'EDR', format0)
            sheet.write(count, 1, dat[count][1], format0)
            sheet.write(count, 2, dat[count][3], format0)
            sheet.write(count, 3, dat[count][2], format0)
            sheet.write(count, 4, lines['start_date'], format0)
            sheet.write(count, 5, lines['end_date'], format0)
            sheet.write(count, 6, str(int(days)).zfill(4), format0)
            sum += int(dat[count][4])
            sheet.write(count, 7, dat[count][4], format0)
            sheet.write(count, 8, '0.0000', format0)
            sheet.write(count, 9, leaves, format0)
        count += 1
        company = self.env.company
        sheet.set_column(1, 1, 14)
        sheet.set_column(2, 2, 12)
        sheet.set_column(3, 3, 16)
        sheet.set_column(4, 4, 9)
        sheet.set_column(5, 5, 9)
        sheet.write(count, 0, 'SCR', format0)
        sheet.write(count, 1, company.company_registry, format0)
        sheet.write(count, 2, company.bank_ids[0].bank_id.routing_code, format0)
        sheet.write(count, 3, lines['date'], format0)
        time = str(lines['date']).split(' ')
        time = time[1].split(':')
        sheet.write(count, 4, time[0] + time[1], format0)
        monthyear = lines['end_date']
        monthyear = str(monthyear).split('-')
        monthyear = str(monthyear[1]) + str(monthyear[0])
        sheet.write(count, 5, monthyear, format0)
        sheet.write(count, 6, count, format0)
        sheet.write(count, 7, sum, format0)
        sheet.write(count, 8, 'AED', format0)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
