# -*- coding: utf-8 -*-
from datetime import date, datetime
import pytz

from odoo.exceptions import UserError
from odoo import models, fields, api, _


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
            self.days = 1+(date(year=int(end[0]), month=int(end[1]), day=int(end[2]))
                         - date(year=int(start[0]), month=int(start[1]), day=int(start[2]))).days
            if start[1] == end[1]:
                self.salary_month = start[1]

    @api.multi
    def print_xlsx(self):
        company = self.env['res.company']._company_default_get('wps.wizard')
        if not company.company_registry:
            raise UserError(_('Please Set Company Registry Number First'))
        users = self.env['hr.employee'].search([])
        flags = {'labour_card_number': True, 'salary_card_number': True, 'agent_id': True}
        for user in users:
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
        slips = self.env['report.wps_xlsx.xlsx'].get_data(self.start_date, self.end_date)
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
        for bank in company.bank_ids:
            if not bank.bank_id.routing_code:
                raise UserError(_('Configure Your Bank\'s Routing Code In Accounting Dashboard'))
        datas = {
            'context': self._context
        }
        self.write({
            'date': date,
            'time': time
        })
        return self.env.ref('uae_wps_report.wps_xlsx').report_action(self, data=datas)
