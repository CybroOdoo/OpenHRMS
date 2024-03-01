# -*- coding: utf-8 -*-
#############################################################################

#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: ASWIN A K (odoo@cybrosys.com)
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
import pytz
import json
from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import date_utils, io, xlsxwriter


class WpsReport(models.TransientModel):
    """
        Wizard for generating UAE WPS Report.
    """
    _name = 'wps.report'
    _description = 'Wps Report Wizard'

    start_date = fields.Date(
        string='Start Date',
        required=True,
        help="Start date of the period for the report")
    end_date = fields.Date(
        string="End Date",
        required=True,
        help="End date of the period for the report")
    days = fields.Integer(
        string="Days of Payment",
        readonly=True, store=True,
        help="Number of days included in the payment period")
    salary_month = fields.Selection(
        [
            ('01', 'January'),
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
            ('12', 'December')],
        string="Month of Salary",
        readonly=True,
        help="Month for which the salary is being processed")

    @api.onchange('start_date', 'end_date')
    def _onchange_date_validation(self):
        """
            Validate the start and end dates.
        """
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            self.days = 1 + (
                    date(year=int(end[0]), month=int(end[1]), day=int(end[2]))
                    - date(year=int(start[0]), month=int(start[1]),
                           day=int(start[2]))).days
            if start[1] == end[1]:
                self.salary_month = start[1]

    def action_print_xlsx(self):
        """
            It is the function for the print button click.
            This function checks if all employees have the required fields set.
        """
        company = self.env.company
        if not company.company_registry:
            raise UserError(_('Please Set Company Registry Number First'))
        employees = self.env['hr.employee'].search([])
        flags = {
            'labour_card_number': True,
            'salary_card_number': True,
            'agent_id': True
        }
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
            raise UserError(_(
                'Please Set Salary Card Number /'
                ' Account Number of All Employees'))
        if not flags['agent_id']:
            raise UserError(_(
                'Please Set Employee Card Number of All Employees'))
        if not self.env['res.users'].browse(self.env.uid).tz:
            raise UserError(_('Please Set a User Timezone'))
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            if not start[1] == end[1]:
                raise UserError(_('The Dates Can of Same Month Only'))
        slips = self.env['wps.report'].get_data(self.start_date, self.end_date)
        if not slips:
            raise UserError(_(
                'There are no payslip Created for the selected month'))
        user = self.env['res.users'].browse(self.env.uid)
        current_date = datetime.now()
        current_time = datetime.now()
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            current_date = pytz.utc.localize(datetime.now()).astimezone(tz)
            current_time = pytz.utc.localize(datetime.now()).astimezone(tz)
        if not company.employer_id:
            raise UserError(_('Configure Your Company Employer ID'))
        if not company.bank_ids:
            raise UserError(_('Configure Your Bank In Accounting Dashboard'))

        datas = {
            'context': self._context,
            'date': current_date,
            'time': current_time,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'wps.report',
                     'options': json.dumps(
                         datas, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Uae wps Report'
                     },
            'report_type': 'wps_xlsx'
        }

    def get_data(self, start, end):
        """Retrieve data for the given date range."""
        cr = self._cr
        slips = self.env['hr.payslip'].search(
            ['&', ('date_from', '<=', start),
             ('date_to', '>=', end)])
        if not slips:
            return False
        ids = ''
        for slip in slips:
            if ids:
                ids = ids + ',' + str(slip.id)
            else:
                ids = ids + str(slip.id)
        language = self.env.context['lang']
        query = """select hr_employee.id,labour_card_number, salary_card_number,
            agent_id, hr_payslip_line.amount 
            from hr_employee join hr_payslip_line 
            on hr_employee.id = hr_payslip_line.employee_id 
            where hr_payslip_line.name = (
            """ + "'{\"" + language + "\": " + "\"Net Salary" + "\"}'" + """) 
            and hr_payslip_line.slip_id in(""" + ids + """) """
        cr.execute(query)
        data = cr.fetchall()
        return data

    def get_days(self, emp_id, start, end):
        """Calculate the total number of days worked."""
        slip = self.env['hr.payslip'].search(
            ['&', ('employee_id', '=', emp_id),
             ('date_from', '=', start),
             ('date_to', '=', end)])
        days = self.env['hr.payslip.worked.days'].search(
            [('payslip_id', '=', slip.id)])
        total_days = sum(rec.number_of_days for rec in days)
        return total_days

    def get_leaves(self, emp_id, start, end):
        """Calculate the total number of leaves taken."""
        leaves = self.env['hr.leave'].search(
            ['&', ('employee_id', '=', emp_id),
             ('date_from', '>=', start),
             ('date_to', '<=', end),
             ('holiday_status_id', '=', 4)]).number_of_days
        return leaves * -1

    def get_xlsx_report(self, lines, response):
        """Generate the XLSX report based on the provided data."""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        format0 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('SIF Report')
        # Set column widths
        column_widths = [14, 12, 16, 9, 9]
        for i, width in enumerate(column_widths):
            sheet.set_column(i+1, i+1, width)
        data = [list(da) for da in self.get_data(lines['start_date'], lines['end_date'])]
        for each_data in data:
            each_data[3] = self.env['res.bank'].browse(each_data[3]).routing_code
        sum_count = 0
        for count, each_data in enumerate(data):
            days = self.get_days(each_data[0], lines['start_date'], lines['end_date'])
            leaves = self.get_leaves(each_data[0], lines['start_date'],
                                     lines['end_date'])
            # Batch write the data
            data_to_write = [
                ['EDR', each_data[1], each_data[3], each_data[2], lines['start_date'],
                 lines['end_date'],
                 str(int(days)).zfill(4), each_data[4], '0.0000', leaves]
            ]
            sheet.write_row(count, 0, data_to_write[0], format0)
            sum_count += int(each_data[4])
        length = len(data)
        company = self.env.company
        sheet.write(length, 0, 'SCR', format0)
        sheet.write_row(length, 1, [
            company.company_registry,
            company.bank_ids[0].bank_id.routing_code,
            lines['date']], format0)
        time = str(lines['date']).split(' ')[1].split(':')
        sheet.write(length, 4, time[0] + time[1], format0)
        monthyear = str(lines['end_date']).split('-')[1] + \
                    str(lines['end_date']).split('-')[0]
        sheet.write(length, 5, monthyear, format0)
        sheet.write(length, 6, length, format0)
        sheet.write(length, 7, sum_count, format0)
        sheet.write(length, 8, 'AED', format0)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
