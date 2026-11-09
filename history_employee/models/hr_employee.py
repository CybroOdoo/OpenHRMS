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
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    """Inherited the 'hr.employee' model to add onchange methods and actions to
    record changes in department, job position, hourly cost, and provides access
     to related historical data for HR employees."""
    _inherit = 'hr.employee'

    department_history_ids = fields.One2many('department.history', 'employee_id', string='Job/Department History')
    salary_history_ids = fields.One2many('salary.history', 'employee_id')
    contract_history_ids = fields.One2many('contract.history', 'employee_id')
    hourly_cost_history_ids = fields.One2many('hourly.cost', 'employee_id')

    def write(self, vals):
        """Record history for employee fields when they are changed and saved."""
        track_dict = {}
        for employee in self:
            c_type = getattr(employee, 'contract_type_id', False)
            emp_type = getattr(employee, 'employee_type_id', False)
            track_dict[employee.id] = {
                'department_id': employee.department_id.id,
                'department_name': employee.department_id.name,
                'job_id': employee.job_id.id,
                'job_name': employee.job_id.name,
                'hourly_cost': employee.hourly_cost,
                'wage': getattr(employee, 'wage', False),
                'contract_date_start': getattr(employee, 'contract_date_start', False),
                'contract_date_end': getattr(employee, 'contract_date_end', False),
                'contract_type_id': c_type.id if c_type else False,
                'contract_type_name': c_type.name if c_type else False,
                'employee_type_id': emp_type.id if emp_type else False,
                'employee_type_name': emp_type.name if emp_type else False,
            }

        res = super().write(vals)

        for employee in self:
            old_vals = track_dict[employee.id]
            
            if 'department_id' in vals and old_vals['department_id'] != employee.department_id.id:
                new_val = employee.department_id.name
                latest = self.env['department.history'].sudo().search([('employee_id', '=', employee.id), ('changed_field', '=', 'Department')], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['department.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'changed_field': 'Department',
                            'current_value': old_vals['department_name']
                        })
                    self.env['department.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Department',
                        'current_value': new_val
                    })
                
            if 'job_id' in vals and old_vals['job_id'] != employee.job_id.id:
                new_val = employee.job_id.name
                latest = self.env['department.history'].sudo().search([('employee_id', '=', employee.id), ('changed_field', '=', 'Job Position')], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['department.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'changed_field': 'Job Position',
                            'current_value': old_vals['job_name']
                        })
                    self.env['department.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Job Position',
                        'current_value': new_val
                    })
                
            if 'hourly_cost' in vals and old_vals['hourly_cost'] != employee.hourly_cost:
                new_val = employee.hourly_cost
                latest = self.env['hourly.cost'].sudo().search([('employee_id', '=', employee.id)], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['hourly.cost'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'current_value': str(old_vals['hourly_cost'])
                        })
                    self.env['hourly.cost'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'current_value': str(new_val)
                    })
                
            if 'wage' in vals and old_vals['wage'] != getattr(employee, 'wage', False):
                new_val = getattr(employee, 'wage', False)
                latest = self.env['salary.history'].sudo().search([('employee_id', '=', employee.id)], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['salary.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'current_value': str(old_vals['wage'])
                        })
                    self.env['salary.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'current_value': str(new_val),
                    })
                
            if 'contract_date_start' in vals and old_vals['contract_date_start'] != getattr(employee, 'contract_date_start', False):
                new_val = getattr(employee, 'contract_date_start', False)
                latest = self.env['contract.history'].sudo().search([('employee_id', '=', employee.id), ('changed_field', '=', 'Start Date')], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'changed_field': 'Start Date',
                            'current_value': str(old_vals['contract_date_start'])
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Start Date',
                        'current_value': str(new_val),
                    })
                
            if 'contract_date_end' in vals and old_vals['contract_date_end'] != getattr(employee, 'contract_date_end', False):
                new_val = getattr(employee, 'contract_date_end', False)
                latest = self.env['contract.history'].sudo().search([('employee_id', '=', employee.id), ('changed_field', '=', 'End Date')], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'changed_field': 'End Date',
                            'current_value': str(old_vals['contract_date_end'])
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'End Date',
                        'current_value': str(new_val),
                    })
                
            if 'contract_type_id' in vals and old_vals['contract_type_id'] != (getattr(employee, 'contract_type_id', False).id if getattr(employee, 'contract_type_id', False) else False):
                ctype = getattr(employee, 'contract_type_id', False)
                new_val = ctype.name if ctype else False
                latest = self.env['contract.history'].sudo().search([('employee_id', '=', employee.id), ('changed_field', '=', 'Contract Type')], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'changed_field': 'Contract Type',
                            'current_value': old_vals['contract_type_name']
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Contract Type',
                        'current_value': str(new_val) if new_val else False,
                    })

            if 'employee_type_id' in vals and old_vals['employee_type_id'] != (getattr(employee, 'employee_type_id', False).id if getattr(employee, 'employee_type_id', False) else False):
                etype = getattr(employee, 'employee_type_id', False)
                new_val = etype.name if etype else False
                latest = self.env['contract.history'].sudo().search([('employee_id', '=', employee.id), ('changed_field', '=', 'Employee Type')], order='id desc', limit=1)
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(employee.id),
                            'employee_id': employee.id,
                            'employee_name': employee.name,
                            'updated_date': (employee.create_date.date() if employee.create_date else fields.Date.today()),
                            'changed_field': 'Employee Type',
                            'current_value': old_vals['employee_type_name']
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(employee.id),
                        'employee_id': employee.id,
                        'employee_name': employee.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Employee Type',
                        'current_value': str(new_val) if new_val else False,
                    })

        return res

    @api.model
    def get_employee_history_timeline(self, employee_id):
        """Aggregate history from all 4 models and compute old -> new values."""
        if not self.env.user.has_group('hr.group_hr_user'):
            return []
        history_items = []

        emp = self.browse(employee_id)
        currency = (emp.company_id.currency_id or self.env.company.currency_id) if emp else self.env.company.currency_id
        symbol = currency.symbol or '₹'
        pos = currency.position or 'before'

        def fmt_currency(val):
            """Format a stored history value as currency, falling back to
            a dash when there's no usable numeric value to show."""
            try:
                fval = float(val)
                formatted = f"{fval:,.2f}"
                return f"{formatted} {symbol}" if pos == 'after' else f"{symbol}{formatted}"
            except (ValueError, TypeError):
                # No previous value exists yet (first time this field is
                # ever set) - show a dash instead of the literal word "None".
                return str(val) if val else "—"

        def fmt_diff(diff, pct):
            """Format the numeric difference and percentage change with the
            currency symbol and appropriate +/- sign."""
            sign = "+" if diff > 0 else ""
            diff_abs = abs(diff)
            formatted = f"{diff_abs:,.2f}"
            diff_fmt = f"{formatted} {symbol}" if pos == 'after' else f"{symbol}{formatted}"
            return f"{sign}{diff_fmt} ({sign}{pct:,.2f}%)"

        def fmt_value(val):
            """Format a stored history value for display. Handle 'False' or
            'None' strings so they display as 'None'."""
            if not val or str(val) in ('False', 'None'):
                return 'None'
            return str(val)

        def fmt_date_val(val, is_end_date=False):
            """Format a stored date string as DD Mon YYYY for display."""
            if not val or str(val).strip() in ('False', 'None', ''):
                return 'Open-ended' if is_end_date else 'None'
            try:
                from datetime import datetime, date
                if isinstance(val, (datetime, date)):
                    return val.strftime('%d %b %Y')
                parts = str(val).split('-')
                if len(parts) == 3:
                    return date(int(parts[0]), int(parts[1]), int(parts[2])).strftime('%d %b %Y')
            except Exception as err:
                _logger.debug("Date format exception for %s: %s", val, err)
            return str(val)

        def fmt_time(dt):
            """Format a datetime as a localized 12-hour time string for
            display on a history card, or an empty string if unset."""
            if not dt:
                return ''
            return fields.Datetime.context_timestamp(self, dt).strftime('%I:%M %p')

        # 1. Salary History
        salaries = self.env['salary.history'].search([('employee_id', '=', employee_id)],
                                                     order='updated_date asc, id asc')
        prev_salary_val = None
        for s in salaries:
            curr_val = s.current_value
            curr_float = 0.0
            prev_float = 0.0
            try:
                curr_float = float(curr_val)
                if prev_salary_val is not None:
                    prev_float = float(prev_salary_val)
            except ValueError as err:
                _logger.debug("Salary float conversion error: %s", err)

            subtitle = ""
            subtitle_color = '#16a34a'
            subtitle_bg = '#dcfce7'
            if prev_salary_val is not None and prev_float > 0 and curr_float > 0:
                diff = curr_float - prev_float
                pct = (diff / prev_float) * 100
                subtitle = fmt_diff(diff, pct)
                if diff < 0:
                    subtitle_color = '#dc2626'  # decrease: red
                    subtitle_bg = '#fee2e2'

            # The very first salary ever recorded for this employee is the
            # starting baseline (e.g. the value seeded by demo/import data),
            # not a "change" the user made - so it isn't shown as its own
            # card. It's only kept to compute the diff for the next entry.
            if prev_salary_val is not None:
                history_items.append({
                    'id': f'salary_{s.id}',
                    'record_id': s.id,
                    'category': 'SALARY',
                    'category_label': 'SALARY',
                    'date': s.updated_date.strftime('%d %b %Y') if s.updated_date else '',
                    'time': fmt_time(s.create_date),
                    'sort_date': s.create_date,
                    'title': f"{fmt_currency(prev_salary_val)} → {fmt_currency(s.current_value)}",
                    'subtitle': subtitle,
                    'subtitle_color': subtitle_color,
                    'subtitle_bg': subtitle_bg,
                    'author_name': s.create_uid.name if s.create_uid else 'System',
                    'author_id': s.create_uid.id if s.create_uid else False,
                    'icon': 'attach_money',
                    'color': '#22c55e',  # Professional Green
                    'light_color': '#dcfce7',  # Very light green
                    'gradient': 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                })
            prev_salary_val = s.current_value

        # 2. Hourly Cost
        hourlys = self.env['hourly.cost'].search([('employee_id', '=', employee_id)], order='updated_date asc, id asc')
        prev_hourly_val = None
        for h in hourlys:
            curr_val = h.current_value
            curr_float = 0.0
            prev_float = 0.0
            try:
                curr_float = float(curr_val)
                if prev_hourly_val is not None:
                    prev_float = float(prev_hourly_val)
            except ValueError as err:
                _logger.debug("Salary float conversion error: %s", err)

            subtitle = ""
            subtitle_color = '#16a34a'
            subtitle_bg = '#dcfce7'
            if prev_hourly_val is not None and prev_float > 0 and curr_float > 0:
                diff = curr_float - prev_float
                pct = (diff / prev_float) * 100
                subtitle = fmt_diff(diff, pct)
                if diff < 0:
                    subtitle_color = '#dc2626'  # decrease: red
                    subtitle_bg = '#fee2e2'

            # Same rule as salary: the first-ever hourly cost is the
            # baseline, not a change - skip its own card.
            if prev_hourly_val is not None:
                history_items.append({
                    'id': f'hourly_{h.id}',
                    'record_id': h.id,
                    'category': 'HOURLY COST',
                    'category_label': 'HOURLY COST',
                    'date': h.updated_date.strftime('%d %b %Y') if h.updated_date else '',
                    'time': fmt_time(h.create_date),
                    'sort_date': h.create_date,
                    'title': f"{fmt_currency(prev_hourly_val)} → {fmt_currency(h.current_value)}",
                    'subtitle': subtitle,
                    'subtitle_color': subtitle_color,
                    'subtitle_bg': subtitle_bg,
                    'author_name': h.create_uid.name if h.create_uid else 'System',
                    'author_id': h.create_uid.id if h.create_uid else False,
                    'icon': 'schedule',
                    'color': '#a855f7',  # Professional Purple
                    'light_color': '#f3e8ff',  # Very light purple
                    'gradient': 'linear-gradient(135deg, #a855f7 0%, #9333ea 100%)',
                })
            prev_hourly_val = h.current_value

        # 3. Contract History
        contracts = self.env['contract.history'].search([('employee_id', '=', employee_id)],
                                                        order='updated_date asc, id asc')
        contract_prevs = {}
        for c in contracts:
            field = c.changed_field or 'Contract'
            is_start = field == 'Start Date'
            is_end = field == 'End Date'
            # First time this particular field (Start Date/End Date/...) is
            # recorded is the baseline, not a change - skip its own card.
            if field in contract_prevs:
                old_raw = contract_prevs[field]
                new_raw = c.current_value

                if is_start or is_end:
                    old_disp = fmt_date_val(old_raw, is_end_date=is_end)
                    new_disp = fmt_date_val(new_raw, is_end_date=is_end)
                    title = f"{field}: {old_disp} → {new_disp}"
                    category_label = f"CONTRACT • {field.upper()}"
                    icon = 'calendar_today' if is_start else 'calendar_clock'
                    subtitle = field
                    subtitle_color = '#c2410c' if is_end else '#ea580c'
                    subtitle_bg = '#fee2e2' if is_end else '#ffedd5'
                else:
                    old_disp = fmt_value(old_raw)
                    new_disp = fmt_value(new_raw)
                    title = f"{field}: {old_disp} → {new_disp}" if field != 'Contract' else f"{old_disp} → {new_disp}"
                    category_label = f"CONTRACT • {field.upper()}"
                    icon = 'badge' if 'Type' in field else 'article'
                    subtitle = field
                    subtitle_color = '#d97706'
                    subtitle_bg = '#fef3c7'

                history_items.append({
                    'id': f'contract_{c.id}',
                    'record_id': c.id,
                    'category': 'CONTRACT',
                    'category_label': category_label,
                    'field_name': field,
                    'date': c.updated_date.strftime('%d %b %Y') if c.updated_date else '',
                    'time': fmt_time(c.create_date),
                    'sort_date': c.create_date,
                    'title': title,
                    'subtitle': subtitle,
                    'subtitle_color': subtitle_color,
                    'subtitle_bg': subtitle_bg,
                    'author_name': c.create_uid.name if c.create_uid else 'System',
                    'author_id': c.create_uid.id if c.create_uid else False,
                    'icon': icon,
                    'color': '#f97316',  # Professional Orange
                    'light_color': '#ffedd5',  # Very light orange
                    'gradient': 'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
                })
            contract_prevs[field] = c.current_value

        # 4. Job / Department History
        deps = self.env['department.history'].search([('employee_id', '=', employee_id)],
                                                     order='updated_date asc, id asc')
        dep_prevs = {}
        for d in deps:
            field = d.changed_field or 'Job/Department'
            is_dept = field == 'Department'
            # First time this field (Department/Job Position) is recorded
            # is the baseline, not a change - skip its own card.
            if field in dep_prevs:
                old_disp = fmt_value(dep_prevs[field])
                new_disp = fmt_value(d.current_value)
                title = f"{field}: {old_disp} → {new_disp}"
                category_label = field.upper()
                subtitle = field
                subtitle_color = '#2563eb' if is_dept else '#0284c7'
                subtitle_bg = '#dbeafe' if is_dept else '#e0f2fe'

                history_items.append({
                    'id': f'dep_{d.id}',
                    'record_id': d.id,
                    'category': 'JOB/DEPT',
                    'category_label': category_label,
                    'field_name': field,
                    'date': d.updated_date.strftime('%d %b %Y') if d.updated_date else '',
                    'time': fmt_time(d.create_date),
                    'sort_date': d.create_date,
                    'title': title,
                    'subtitle': subtitle,
                    'subtitle_color': subtitle_color,
                    'subtitle_bg': subtitle_bg,
                    'author_name': d.create_uid.name if d.create_uid else 'System',
                    'author_id': d.create_uid.id if d.create_uid else False,
                    'icon': 'work',
                    'color': '#3b82f6',  # Professional Blue
                    'light_color': '#dbeafe',  # Very light blue
                    'gradient': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                })
            dep_prevs[field] = d.current_value

        # Sort combined history items by date descending, then ID descending
        def get_sort_key(item):
            """Build a (datetime, record_id) sort key for a history item,
            normalizing sort_date to a comparable datetime regardless of
            whether it was stored as a date or a datetime."""
            d = item['sort_date']
            from datetime import datetime, date
            if isinstance(d, datetime):
                dt = d
            elif isinstance(d, date):
                dt = datetime(d.year, d.month, d.day)
            else:
                dt = datetime.min
            return (dt, item.get('record_id', 0))

        history_items.sort(key=get_sort_key, reverse=True)

        # Remove sort_date before sending to frontend as it's not JSON serializable if date/datetime object
        for item in history_items:
            del item['sort_date']

        return history_items


class HrEmployeePublic(models.Model):
    """Inherited the 'hr.employee.public' model to provide the timeline
    history helper method for public employee views."""
    _inherit = 'hr.employee.public'

    @api.model
    def get_employee_history_timeline(self, employee_id):
        """Allow Public Employee view to call timeline helper seamlessly."""
        return self.env['hr.employee'].get_employee_history_timeline(employee_id)

