# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
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
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models, tools, _
from datetime import datetime, time, timedelta


class HrPayslip(models.Model):
    """Inherits from the hr.payslip model to extend its functionality for
        calculating worked days and hours for employee payroll processing."""
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """@param contracts: list of versions/contracts
        @return: returns a list of dict containing the input that should be
         applied for the given contract between date_from and date_to"""

        def was_on_leave_interval(employee_id, date_from, date_to):
            date_from_str = fields.Datetime.to_string(date_from)
            date_to_str = fields.Datetime.to_string(date_to)
            return self.env['hr.leave'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('date_from', '<=', date_from_str),
                ('date_to', '>=', date_to_str)
            ], limit=1)
        res = []
        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        uom_hour = self.env.ref('product.product_uom_hour', raise_if_not_found=False)
        contracts_without_shifts = self.env['hr.version']
        # Ensure date_from and date_to are date objects
        date_from_obj = fields.Date.from_string(date_from)
        date_to_obj = fields.Date.from_string(date_to)
        for contract in contracts:
            # Find shifts that overlap with the payslip period on the Employee profile
            relevant_shifts = contract.employee_id.shift_schedule.filtered(
                lambda s: s.start_date <= date_to_obj and s.end_date >= date_from_obj
            )
            # If no shifts are scheduled for this period, fallback to standard working hours
            if not relevant_shifts:
                contracts_without_shifts |= contract
                continue
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
            nb_of_days = (date_to_obj - date_from_obj).days + 1
            start_dt = datetime.combine(date_from_obj, time.min)
            for day in range(nb_of_days):
                current_day_dt = start_dt + timedelta(days=day)
                current_date = current_day_dt.date()
                # Check if a shift applies to this specific date
                active_shift = relevant_shifts.filtered(lambda s: s.start_date <= current_date <= s.end_date)
                # Use shift calendar if exists, else fallback to default contract calendar
                calendar = active_shift[:1].hr_shift if active_shift else contract.resource_calendar_id
                if calendar:
                    working_intervals_on_day = calendar._get_day_work_intervals(current_day_dt)
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
                        leaves[holiday.holiday_status_id.name]['number_of_hours'] += hours
                    else:
                        leaves[holiday.holiday_status_id.name] = {
                            'name': holiday.holiday_status_id.name,
                            'sequence': 5,
                            'code': holiday.holiday_status_id.code or 'GLOBAL',
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
        # Inject amount into worked_day_dict for shift-based lines
        contracts_dict = {c.id: c for c in contracts}
        contract_days = {}
        for d in res:
            cid = d.get('contract_id')
            if cid:
                contract_days[cid] = contract_days.get(cid, 0.0) + d.get('number_of_days', 0.0)
        for worked_day_dict in res:
            contract_id = worked_day_dict.get('contract_id')
            contract = contracts_dict.get(contract_id)
            if contract and hasattr(self, '_prepare_worked_day_line'):
                total_days = contract_days.get(contract_id, 30.0)
                self._prepare_worked_day_line(worked_day_dict, contract, date_from, date_to, total_days)
        if contracts_without_shifts:
            res.extend(super(HrPayslip, self).get_worked_day_lines(contracts_without_shifts, date_from, date_to))
        return res
