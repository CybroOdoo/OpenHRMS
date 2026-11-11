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
from odoo import api, fields, models
from odoo.fields import Domain


class HrEmployee(models.Model):
    """Inheriting hr_employee"""
    _inherit = 'hr.employee'

    wage_type = fields.Selection(
        related='version_id.wage_type',
        readonly=False,
        inherited=True,
        groups="hr.group_hr_user",
        help="Wage type of the employee.",
    )
    hourly_wage = fields.Monetary(
        related='version_id.hourly_wage',
        readonly=False,
        inherited=True,
        groups="hr.group_hr_manager",
        help="Employee's hourly gross wage.",
    )

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        super()._onchange_contract_template_id()
        if self.contract_template_id:
            template = self.contract_template_id
            if template.wage_type:
                self.wage_type = template.wage_type
            self.hourly_wage = template.hourly_wage
            for field_name in [
                'hra', 'da', 'travel_allowance', 'meal_allowance',
                'medical_allowance', 'other_allowance'
            ]:
                if hasattr(template, field_name):
                    val = getattr(template, field_name)
                    self[field_name] = val
                    if self.version_id and hasattr(self.version_id, field_name):
                        self.version_id[field_name] = val

    def generate_work_entries(self, date_start, date_stop):
        """Generate work entries using native version mechanism"""
        return super().generate_work_entries(date_start, date_stop)

    def _get_contracts(self, date_from, date_to, states=['open', 'probation'],
                       kanban_state=False):
        """Returns the contracts (versions) of the employee between date_from and
        date_to"""
        state_domain = [('state', 'in', states)]
        if kanban_state:
            state_domain = Domain.AND(
                [state_domain, [('kanban_state', 'in', kanban_state)]])
        return self.env['hr.version'].search(
            Domain.AND([[('employee_id', 'in', self.ids)],
                        state_domain,
                        [('contract_date_start', '<=', date_to),
                         '|',
                         ('contract_date_end', '=', False),
                         ('contract_date_end', '>=', date_from)]]))
