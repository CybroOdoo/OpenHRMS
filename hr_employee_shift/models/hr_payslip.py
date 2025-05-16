# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from datetime import timedelta
from odoo import api, fields, models, tools, _
from datetime import datetime


class HrPayslip(models.Model):
    """Inherits from the hr.payslip model to extend its functionality for
        calculating worked days and hours for employee payroll processing."""
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """@param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be
         applied for the given contract between date_from and date_to"""

        def was_on_leave_interval(employee_id, date_from, date_to):
            date_from = fields.Datetime.to_string(date_from)
            date_to = fields.Datetime.to_string(date_to)
            return self.env['hr.leave'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('date_from', '<=', date_from),
                ('date_to', '>=', date_to)
            ], limit=1)
        res = []
        uom_day = self.env.ref('product.product_uom_day',
                               raise_if_not_found=False)
        for contract in contract_ids:
            uom_hour = self.env.ref('product.product_uom_hour',
                                    raise_if_not_found=False)
            interval_data = []
            holidays = self.env['hr.leave']
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}
            for days in contract.shift_schedule:
                start_date = datetime.datetime.strptime(str(days.start_date),
                                                        tools.DEFAULT_SERVER_DATE_FORMAT)
                end_date = datetime.datetime.strptime(str(days.end_date),
                                                      tools.DEFAULT_SERVER_DATE_FORMAT)
                nb_of_days = (days.end_date - days.start_date).days + 1
                for day in range(0, nb_of_days):
                    working_intervals_on_day = days.hr_shift._get_day_work_intervals(
                        start_date + timedelta(days=day))
                    for interval in working_intervals_on_day:
                        interval_data.append(
                            (interval,
                             was_on_leave_interval(contract.employee_id.id,
                                                   interval[0], interval[1])))
            for interval, holiday in interval_data:
                holidays |= holiday
                hours = (interval[1] - interval[0]).total_seconds() / 3600.0
                if holiday:
                    if holiday.holiday_status_id.name in leaves:
                        leaves[holiday.holiday_status_id.name][
                            'number_of_hours'] += hours
                    else:
                        leaves[holiday.holiday_status_id.name] = {
                            'name': holiday.holiday_status_id.name,
                            'sequence': 5,
                            'code': holiday.holiday_status_id.name,
                            'number_of_days': 0.0,
                            'number_of_hours': hours,
                            'contract_id': contract.id,
                        }
                else:
                    attendances['number_of_hours'] += hours
            leaves = [value for key, value in leaves.items()]
            for data in [attendances] + leaves:
                data['number_of_days'] = uom_hour._compute_quantity(
                    data['number_of_hours'], uom_day) \
                    if uom_day and uom_hour \
                    else data['number_of_hours'] / 8.0
                res.append(data)
        return res
