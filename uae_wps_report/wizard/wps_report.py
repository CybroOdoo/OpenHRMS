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
import io
import json
from datetime import date, datetime
import pytz
import xlsxwriter
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.tools import json_default


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
            else:
                self.salary_month = False

    def action_print_xlsx(self):
        """
            It is the function for the print button click.
            This function checks if all employees have the required fields set.
        """
        company = self.env.company
        if not company.company_registry:
            raise UserError(_('Please Set Company Registry Number First'))
        user = self.env['res.users'].browse(self.env.uid)
        if not user.tz:
            raise UserError(_('Please Set a User Timezone'))
        if not company.employer_id:
            raise UserError(_('Configure Your Company Employer ID'))
        if not company.wps_agent_id and not company.bank_ids:
            raise UserError(_('Configure Your Bank or WPS Agent In Company Settings'))
        if self.start_date and self.end_date:
            start = str(self.start_date).split('-')
            end = str(self.end_date).split('-')
            if not start[1] == end[1]:
                raise UserError(_('The Dates Can of Same Month Only'))
        slips = self.get_data(self.start_date, self.end_date)
        if not slips:
            raise UserError(_(
                'There are no payslip Created for the selected month'))

        employee_ids = [s[0] for s in slips]
        employees = self.env['hr.employee'].browse(employee_ids)
        missing_labour = employees.filtered(lambda e: not e.labour_card_number)
        if missing_labour:
            raise UserError(_('Please Set Labour Card Number for: %s') % ', '.join(missing_labour.mapped('name')))
        missing_salary = employees.filtered(lambda e: not e.salary_card_number)
        if missing_salary:
            raise UserError(_('Please Set Salary Card Number / Account Number for: %s') % ', '.join(missing_salary.mapped('name')))
        missing_agent = employees.filtered(lambda e: not e.agent_id)
        if missing_agent:
            raise UserError(_('Please Set Agent/Bank for: %s') % ', '.join(missing_agent.mapped('name')))

        current_date = datetime.now()
        current_time = datetime.now()
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            current_date = pytz.utc.localize(datetime.now()).astimezone(tz)
            current_time = pytz.utc.localize(datetime.now()).astimezone(tz)

        datas = {
            'context': self.env.context,
            'date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
            'time': current_time.strftime('%H:%M:%S'),
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'wps.report',
                     'options': json.dumps(
                         datas, default=json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Uae wps Report'
                     },
            'report_type': 'wps_xlsx'
        }

    def get_data(self, start, end):
        """Retrieve data for the given date range using ORM search."""
        slips = self.env['hr.payslip'].search([
            ('date_from', '<=', start),
            ('date_to', '>=', end),
        ])
        if not slips:
            return False
        lines = self.env['hr.payslip.line'].search([
            ('slip_id', 'in', slips.ids),
            ('code', '=', 'NET'),
        ])
        data = []
        for line in lines:
            emp = line.employee_id
            routing = emp.agent_id.routing_code if emp.agent_id else ''
            data.append([
                emp.id,
                emp.labour_card_number or '',
                emp.salary_card_number or '',
                routing,
                line.total or line.amount or 0.0,
            ])
        return data

    def get_days(self, emp_id, start, end):
        """Calculate the total number of days worked."""
        slip = self.env['hr.payslip'].search([
            ('employee_id', '=', emp_id),
            ('date_from', '<=', end),
            ('date_to', '>=', start),
        ], limit=1)
        if not slip:
            return 0
        total_days = 0
        if hasattr(slip, 'worked_days_line_ids') and slip.worked_days_line_ids:
            total_days = sum(rec.number_of_days for rec in slip.worked_days_line_ids)
        else:
            days = self.env['hr.payslip.worked.days'].search(
                [('payslip_id', '=', slip.id)])
            total_days = sum(rec.number_of_days for rec in days)
        if not total_days and start and end:
            s = fields.Date.from_string(start)
            e = fields.Date.from_string(end)
            if s and e:
                total_days = (e - s).days + 1
        return int(total_days or 0)

    def get_leaves(self, emp_id, start, end):
        """Calculate the total number of leaves taken."""
        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', emp_id),
            ('date_from', '>=', start),
            ('date_to', '<=', end),
        ])
        if leaves:
            return int(sum(leave.number_of_days for leave in leaves))
        return 0

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
        raw_data = self.get_data(lines['start_date'], lines['end_date'])
        data = [list(da) for da in raw_data] if raw_data else []
        for each_data in data:
            if each_data[3]:
                each_data[3] = str(each_data[3]).zfill(9)
            else:
                each_data[3] = '000000000'
        sum_count = 0.0
        for count, each_data in enumerate(data):
            days = self.get_days(each_data[0], lines['start_date'], lines['end_date']) or 0
            leaves = self.get_leaves(each_data[0], lines['start_date'],
                                     lines['end_date']) or 0
            salary = float(each_data[4] or 0.0)
            # Batch write the data
            data_to_write = [
                ['EDR', each_data[1], each_data[3], each_data[2], lines['start_date'],
                 lines['end_date'],
                 str(int(days)).zfill(4), round(salary, 2), '0.0000', int(leaves)]
            ]
            sheet.write_row(count, 0, data_to_write[0], format0)
            sum_count += salary
        length = len(data)
        company = self.env.company
        sheet.write(length, 0, 'SCR', format0)
        company_routing = ''
        if company.wps_agent_id and company.wps_agent_id.routing_code:
            company_routing = company.wps_agent_id.routing_code
        elif company.bank_ids:
            first_bank = company.bank_ids[0]
            routing = getattr(first_bank, 'clearing_number', False) or getattr(first_bank, 'routing_code', False) or ''
            company_routing = str(routing).zfill(9) if routing else ''
        if not company_routing:
            company_routing = '000000000'

        date_str = str(lines.get('date', ''))
        creation_date = date_str.split(' ')[0].split('T')[0] if date_str else ''
        sheet.write_row(length, 1, [
            company.company_registry or '',
            company_routing,
            creation_date or lines.get('date', '')], format0)
        time_part = date_str.split('T')[1] if 'T' in date_str else date_str.split(' ')[1] if ' ' in date_str else '00:00:00'
        time_clean = time_part.replace(':', '')[:4]
        sheet.write(length, 4, time_clean, format0)
        monthyear = str(lines['end_date']).split('-')[1] + \
                    str(lines['end_date']).split('-')[0]
        sheet.write(length, 5, monthyear, format0)
        sheet.write(length, 6, length, format0)
        sheet.write(length, 7, round(sum_count, 2), format0)
        sheet.write(length, 8, 'AED', format0)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
