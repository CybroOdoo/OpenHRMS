# -*- coding: utf-8 -*-
from odoo import models
from odoo import _
from odoo.exceptions import UserError


class GenerateSif(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.wps_xlsx.xlsx'

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
        query = """select hr_employee.id,labour_card_number, salary_card_number, agent_id, hr_payslip_line.amount 
from hr_employee join hr_payslip_line 
on hr_employee.id = hr_payslip_line.employee_id 
where hr_payslip_line.name = 'Net Salary' and hr_payslip_line.slip_id in("""+ids+""")"""
        cr.execute(query)
        data = cr.fetchall()
        return data

    def get_days(self, emp_id, start, end):
        slip = self.env['hr.payslip'].search(['&', ('employee_id', '=', emp_id)
                                                 , ('date_from', '=', start)
                                                 , ('date_to', '=', end)])
        days = self.env['hr.payslip.worked_days'].search([('payslip_id', '=', slip.id)]).number_of_days
        return days

    def get_leaves(self, emp_id, start, end):
        leaves = self.env['hr.holidays'].search(['&', ('employee_id', '=', emp_id)
                                                  , ('date_from', '>=', start)
                                                  , ('date_to', '<=', end)
                                                  , ('holiday_status_id', '=', 4)]).number_of_days
        return leaves*-1

    def generate_xlsx_report(self, workbook, data, lines):
        format0 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('SIF Report')
        dat = self.get_data(lines.start_date, lines.end_date)
        if dat == 11:
            raise UserError(_('There is no payslips created for this month'))
        dat = [list(da) for da in dat]
        for da in dat:
            da[3] = self.env['res.bank'].browse(da[3]).routing_code
        count = 0
        sum = 0
        for count in range(0, len(dat)):
            days = self.get_days(dat[count][0], lines.start_date, lines.end_date)
            leaves = self.get_leaves(dat[count][0], lines.start_date, lines.end_date)
            sheet.set_column(1, 1, 14)
            sheet.set_column(2, 2, 12)
            sheet.set_column(3, 3, 16)
            sheet.set_column(4, 4, 9)
            sheet.set_column(5, 5, 9)
            sheet.write(count, 0, 'EDR', format0)
            sheet.write(count, 1, dat[count][1], format0)
            sheet.write(count, 2, dat[count][3], format0)
            sheet.write(count, 3, dat[count][2], format0)
            sheet.write(count, 4, lines.start_date, format0)
            sheet.write(count, 5, lines.end_date, format0)
            sheet.write(count, 6, str(int(days)).zfill(4), format0)
            sum += int(dat[count][4])
            sheet.write(count, 7, dat[count][4], format0)
            sheet.write(count, 8, '0.0000', format0)
            sheet.write(count, 9, leaves, format0)
        count += 1
        company = self.env['res.company']._company_default_get('wps.wizard')
        sheet.set_column(1, 1, 14)
        sheet.set_column(2, 2, 12)
        sheet.set_column(3, 3, 16)
        sheet.set_column(4, 4, 9)
        sheet.set_column(5, 5, 9)
        sheet.write(count, 0, 'SCR', format0)
        sheet.write(count, 1, company.company_registry, format0)
        sheet.write(count, 2, company.bank_ids[0].bank_id.routing_code, format0)
        sheet.write(count, 3, lines.date, format0)
        time = lines.date.split(' ')
        time = time[1].split(':')
        sheet.write(count, 4, time[0]+time[1], format0)
        monthyear = lines.end_date
        monthyear = monthyear.split('-')
        monthyear = str(monthyear[1])+str(monthyear[0])
        sheet.write(count, 5, monthyear, format0)
        sheet.write(count, 6, count, format0)
        sheet.write(count, 7, sum, format0)
        sheet.write(count, 8, 'AED', format0)
        # sheet.write(count, 9, leaves, format0)
