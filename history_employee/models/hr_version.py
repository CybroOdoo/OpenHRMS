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
#    This program is distributed in the hope it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#############################################################################
from odoo import fields, models


class HrVersion(models.Model):
    """Extends the 'hr.version' model to add onchange methods to record
    changes in contract-related fields (wage, name, date_start, date_end) and
    stores the historical data in the 'salary.history' and 'contract.history'
    models for HR contracts."""
    _inherit = 'hr.version'

    def write(self, vals):
        """Record history for contract-related fields when they are changed and saved."""
        track_dict = {}
        for record in self:
            # ``contract_type_id`` was available on older contract models;
            # ``employee_type_id`` is the standard model in Odoo 20.
            contract_type = (
                record.contract_type_id
                if 'contract_type_id' in record._fields
                else False
            )
            emp_type = (
                record.employee_type_id
                if 'employee_type_id' in record._fields
                else False
            )
            track_dict[record.id] = {
                'wage': record.wage,
                'contract_date_start': record.contract_date_start,
                'contract_date_end': record.contract_date_end,
                'contract_type_id': contract_type.id if contract_type else False,
                'contract_type_name': contract_type.name if contract_type else False,
                'employee_type_id': emp_type.id if emp_type else False,
                'employee_type_name': emp_type.name if emp_type else False,
            }

        res = super().write(vals)

        for record in self:
            old_vals = track_dict[record.id]

            if 'wage' in vals and old_vals['wage'] != record.wage:
                new_val = record.wage
                latest = self.env['salary.history'].sudo().search(
                    [('employee_id', '=', record.employee_id.id)],
                    order='id desc',
                    limit=1,
                )
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['salary.history'].sudo().create({
                            'employee': str(record.employee_id.id),
                            'employee_id': record.employee_id.id,
                            'employee_name': record.employee_id.name,
                            'updated_date': (record.create_date.date() if record.create_date else fields.Date.today()),
                            'current_value': str(old_vals['wage']),
                        })
                    self.env['salary.history'].sudo().create({
                        'employee': str(record.employee_id.id),
                        'employee_id': record.employee_id.id,
                        'employee_name': record.employee_id.name,
                        'updated_date': fields.Date.today(),
                        'current_value': str(new_val),
                    })

            if 'contract_date_start' in vals and old_vals['contract_date_start'] != record.contract_date_start:
                new_val = record.contract_date_start
                latest = self.env['contract.history'].sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('changed_field', '=', 'Start Date')],
                    order='id desc',
                    limit=1,
                )
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(record.employee_id.id),
                            'employee_id': record.employee_id.id,
                            'employee_name': record.employee_id.name,
                            'updated_date': (record.create_date.date() if record.create_date else fields.Date.today()),
                            'changed_field': 'Start Date',
                            'current_value': str(old_vals['contract_date_start']),
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(record.employee_id.id),
                        'employee_id': record.employee_id.id,
                        'employee_name': record.employee_id.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Start Date',
                        'current_value': str(new_val),
                    })

            if 'contract_date_end' in vals and old_vals['contract_date_end'] != record.contract_date_end:
                new_val = record.contract_date_end
                latest = self.env['contract.history'].sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('changed_field', '=', 'End Date')],
                    order='id desc',
                    limit=1,
                )
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(record.employee_id.id),
                            'employee_id': record.employee_id.id,
                            'employee_name': record.employee_id.name,
                            'updated_date': (record.create_date.date() if record.create_date else fields.Date.today()),
                            'changed_field': 'End Date',
                            'current_value': str(old_vals['contract_date_end']),
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(record.employee_id.id),
                        'employee_id': record.employee_id.id,
                        'employee_name': record.employee_id.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'End Date',
                        'current_value': str(new_val),
                    })

            if (
                'contract_type_id' in record._fields
                and 'contract_type_id' in vals
                and old_vals['contract_type_id'] != (record.contract_type_id.id if record.contract_type_id else False)
            ):
                new_val = record.contract_type_id.name if record.contract_type_id else False
                latest = self.env['contract.history'].sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('changed_field', '=', 'Contract Type')],
                    order='id desc',
                    limit=1,
                )
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(record.employee_id.id),
                            'employee_id': record.employee_id.id,
                            'employee_name': record.employee_id.name,
                            'updated_date': (record.create_date.date() if record.create_date else fields.Date.today()),
                            'changed_field': 'Contract Type',
                            'current_value': old_vals['contract_type_name'],
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(record.employee_id.id),
                        'employee_id': record.employee_id.id,
                        'employee_name': record.employee_id.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Contract Type',
                        'current_value': str(new_val) if new_val else False,
                    })

            if (
                'employee_type_id' in record._fields
                and 'employee_type_id' in vals
                and old_vals['employee_type_id'] != (record.employee_type_id.id if record.employee_type_id else False)
            ):
                new_val = record.employee_type_id.name if record.employee_type_id else False
                latest = self.env['contract.history'].sudo().search(
                    [('employee_id', '=', record.employee_id.id), ('changed_field', '=', 'Employee Type')],
                    order='id desc',
                    limit=1,
                )
                if not latest or str(latest.current_value) != str(new_val):
                    if not latest:
                        self.env['contract.history'].sudo().create({
                            'employee': str(record.employee_id.id),
                            'employee_id': record.employee_id.id,
                            'employee_name': record.employee_id.name,
                            'updated_date': (record.create_date.date() if record.create_date else fields.Date.today()),
                            'changed_field': 'Employee Type',
                            'current_value': old_vals['employee_type_name'],
                        })
                    self.env['contract.history'].sudo().create({
                        'employee': str(record.employee_id.id),
                        'employee_id': record.employee_id.id,
                        'employee_name': record.employee_id.name,
                        'updated_date': fields.Date.today(),
                        'changed_field': 'Employee Type',
                        'current_value': str(new_val) if new_val else False,
                    })

        return res
